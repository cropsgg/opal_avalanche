from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.security import current_user
from app.core.pii_redaction import redact_user_input, get_pii_redactor
from app.core.encryption import encrypt_user_input
from app.db.session import get_db
from app.db.models import PIIRecord
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.retrieval.assemble import retrieve_packs
from app.agents.drafting_agent import DraftingAgent
from app.agents.statute_agent import StatuteAgent
from app.agents.precedent_agent import PrecedentAgent
from app.agents.limitation_agent import LimitationAgent
from app.agents.risk_agent import RiskAgent
from app.agents.devil_agent import DevilAgent
from app.agents.ethics_agent import EthicsAgent
from app.agents.aggregator import aggregate
from app.verify.checks import verify_comprehensive
from app.db import crud
from app.billing.credits import calculate_and_debit_query_cost


router = APIRouter()


class ChatRequest(BaseModel):
    matterId: UUID
    message: str
    mode: str = Field("general", pattern="^(general|precedent|limitation|draft)$")
    filters: Dict[str, Any] = {}


class Citation(BaseModel):
    authority_id: UUID
    para_ids: List[int]


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation] = []
    runId: UUID
    merkleRoot: Optional[str] = None
    notarization: Optional[Dict[str, Any]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    import structlog
    log = structlog.get_logger()
    
    user_id = user["id"]
    log.info("chat.start", user_id=user_id, mode=req.mode, message_length=len(req.message))
    
    # Step 1: PII Detection and Redaction
    pii_result = redact_user_input(req.message, user_id, mode="placeholder")
    redacted_message = pii_result["redacted_text"]
    
    # Log PII detections for audit (if any found)
    if pii_result["has_pii"]:
        log.warning("chat.pii_detected", 
                   user_id=user_id,
                   pii_count=len(pii_result["pii_detected"]),
                   types=pii_result["summary"]["types_detected"])
        
        # Store PII audit records
        for pii_detection in pii_result["pii_detected"]:
            pii_record = PIIRecord(
                user_id=UUID(user_id),
                pii_type=pii_detection["type"],
                detection_confidence=pii_detection["confidence"],
                redacted_count=1
            )
            # Store encrypted original for audit (high-confidence detections only)
            if pii_detection["confidence"] >= 0.8:
                pii_record.encrypt_original(pii_detection["value"], user_id)
            
            db.add(pii_record)
    
    # Step 2: Pre-flight cost estimation and billing check
    billing_result = await calculate_and_debit_query_cost(
        db, user_id, "", redacted_message, req.mode, req.filters, sources_count=12
    )
    
    if not billing_result["success"]:
        # Create a dummy run ID for billing failure case
        dummy_run_id = uuid4()
        return ChatResponse(
            answer=f"**Insufficient Credits**: You need {billing_result['total_cost']} credits but have {billing_result['current_balance']}. "
                   f"Shortfall: {billing_result['shortfall']} credits.\n\n"
                   f"**Cost Breakdown**: {billing_result['cost_breakdown']['breakdown']}\n\n"
                   f"Please purchase more credits or upgrade your plan to continue.",
            citations=[],
            runId=dummy_run_id,
            merkleRoot=None
        )
    
    # Step 3: Use redacted message for retrieval to avoid PII in search
    packs = await retrieve_packs(db, redacted_message, limit=12, filters=req.filters)
    
    # Initialize all 7 agents
    agents = {
        "statute": StatuteAgent(),
        "precedent": PrecedentAgent(), 
        "limitation": LimitationAgent(),
        "risk": RiskAgent(),
        "devil": DevilAgent(),
        "ethics": EthicsAgent(),
        "drafting": DraftingAgent()
    }
    
    # Run all agents in parallel for better performance
    agent_outputs = {}
    matter_docs = []  # TODO: Load actual matter documents if needed
    
    # Execute all agents
    for agent_name, agent in agents.items():
        try:
            # Use redacted message for agent processing to avoid PII exposure
            output = await agent.run(redacted_message, packs, matter_docs)
            agent_outputs[agent_name] = output
        except Exception as e:
            # Log error but continue with other agents
            import structlog
            log = structlog.get_logger()
            log.error("agent.error", agent=agent_name, error=str(e))
            # Provide fallback output
            agent_outputs[agent_name] = {
                "reasoning": f"Agent {agent_name} encountered an error: {str(e)}",
                "sources": [],
                "confidence": 0.1
            }
    
    # Aggregate all agent outputs using confidence-weighted voting with MWU
    agg = aggregate(agent_outputs, query=redacted_message)
    
    # Extract citations from sources in aggregated result
    citations = []
    for pack in packs:
        if pack.get("authority_id"):
            citations.append(Citation(
                authority_id=pack["authority_id"],
                para_ids=[p.get("para_id", 0) for p in pack.get("paras", [])]
            ))
    
    # Convert citations to format expected by verification
    sources_for_verification = [
        {
            "authority_id": citation.authority_id,
            "para_ids": citation.para_ids
        }
        for citation in citations
    ]
    
    # Verify the aggregated result using comprehensive verification
    verify_report = await verify_comprehensive(agg["answer"], sources_for_verification, packs)
    
    # Persist query and run with agent vote details (store both original and encrypted message)
    q = await crud.create_query(db, matter_id=req.matterId, message=req.message, mode=req.mode, filters_json=req.filters)
    
    # Encrypt and store the original message for audit/compliance
    q.encrypt_message(req.message, user_id)
    
    # Update PII records with query ID for tracking
    if pii_result["has_pii"]:
        await db.execute(text("""
            UPDATE pii_records 
            SET query_id = :query_id 
            WHERE user_id = :user_id 
            AND query_id IS NULL 
            AND created_at >= NOW() - INTERVAL '1 hour'
        """), {"query_id": str(q.id), "user_id": user_id})
    r = await crud.create_run(
        db, 
        query_id=q.id, 
        answer_text=agg["answer"], 
        confidence=agg.get("confidence", 0.0), 
        retrieval_set_json=packs
    )
    
    # Update billing record with actual run ID
    await db.execute(text("""
        UPDATE billing_ledger 
        SET run_id = :run_id 
        WHERE user_id = :user_id 
        AND run_id IS NULL 
        AND created_at >= NOW() - INTERVAL '1 hour'
        ORDER BY created_at DESC 
        LIMIT 1
    """), {"run_id": str(r.id), "user_id": user["id"]})
    
    # Store agent votes for audit trail
    for agent_name, output in agent_outputs.items():
        await crud.create_agent_vote(
            db,
            run_id=r.id,
            agent=agent_name,
            decision_json=output,
            confidence=output["confidence"],
            aligned=(agent_name in agg.get("aligned", [])),
            weights_before=agg.get("weights_before", {}),
            weights_after=agg.get("weights", {})
        )
    
    # Handle verification failure
    if not verify_report["valid"]:
        return ChatResponse(
            answer=f"**Verification Failed**: {verify_report['summary']}\n\n**Issues Detected**:\n" + 
                   "\n".join([f"• {flag}" for flag in verify_report["flags"][:3]]) +
                   "\n\n**Recommendation**: Please refine your query or provide more specific context.",
            citations=[],
            runId=r.id,
            merkleRoot=None
        )
    
    return ChatResponse(
        answer=agg["answer"] + f"\n\n*Verification: {verify_report['verification_level'].title()} confidence ({verify_report['confidence']:.2f})*", 
        citations=citations[:5],  # Limit citations for response size
        runId=r.id, 
        merkleRoot=None
    )


