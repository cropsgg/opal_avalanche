from __future__ import annotations

from typing import Literal, Dict, Any
from uuid import UUID
import tempfile
import os
from pathlib import Path
import structlog

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.security import current_user
from app.db.session import get_db
from app.billing.credits import calculate_and_debit_export_cost
from app.export.to_docx import export_docx
from app.export.to_pdf import export_pdf
from app.export.audit_bundle import write_audit_json
from app.storage.supabase_client import upload_file, get_signed_url

log = structlog.get_logger()
router = APIRouter()


class ExportRequest(BaseModel):
    format: Literal["docx", "pdf", "json"]


class ExportResponse(BaseModel):
    url: str
    format: str
    file_size: int
    cost_credits: int
    expires_at: str


@router.post("/runs/{run_id}/export", response_model=ExportResponse)
async def export_run(
    run_id: UUID, 
    req: ExportRequest, 
    user=Depends(current_user), 
    db: AsyncSession = Depends(get_db)
):
    """
    Export a run to DOCX, PDF, or JSON audit bundle format
    Includes billing integration and signed URL generation
    """
    user_id = user["id"]
    
    log.info("export.start", 
            run_id=str(run_id), 
            format=req.format, 
            user_id=user_id)
    
    try:
        # Step 1: Fetch run data with full audit trail
        run_data = await _fetch_run_data(db, run_id, user_id)
        if not run_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Run not found or access denied"
            )
        
        # Step 2: Calculate and debit export cost
        billing_result = await calculate_and_debit_export_cost(
            db, user_id, str(run_id), req.format, run_data
        )
        
        if not billing_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Required: {billing_result['total_cost']}, "
                       f"Available: {billing_result['current_balance']}"
            )
        
        # Step 3: Generate export file based on format
        export_file_path = await _generate_export_file(run_data, req.format, run_id)
        
        # Step 4: Upload to storage and get signed URL
        storage_path = f"exports/{user_id}/{run_id}.{req.format}"
        upload_success, upload_error = upload_file(
            bucket="exports",
            path=storage_path,
            file_path=export_file_path,
            content_type=_get_content_type(req.format)
        )
        
        if not upload_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload export: {upload_error}"
            )
        
        # Step 5: Generate signed URL (valid for 24 hours)
        signed_url = get_signed_url(
            bucket="exports",
            path=storage_path,
            expires_in=24 * 3600  # 24 hours
        )
        
        # Step 6: Get file size and cleanup temp file
        file_size = os.path.getsize(export_file_path)
        os.unlink(export_file_path)  # Clean up temp file
        
        log.info("export.complete",
                run_id=str(run_id),
                format=req.format,
                file_size=file_size,
                cost_credits=billing_result["total_cost"],
                user_id=user_id)
        
        return ExportResponse(
            url=signed_url,
            format=req.format,
            file_size=file_size,
            cost_credits=billing_result["total_cost"],
            expires_at="24 hours"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error("export.error", 
                 run_id=str(run_id), 
                 format=req.format, 
                 error=str(e),
                 user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export generation failed"
        )


async def _fetch_run_data(db: AsyncSession, run_id: UUID, user_id: str) -> Dict[str, Any]:
    """Fetch complete run data with audit trail for export"""
    
    # Main run query with RLS enforcement
    run_query = """
        SELECT 
            r.id as run_id,
            r.answer_text,
            r.confidence,
            r.retrieval_set_json,
            r.created_at,
            q.id as query_id,
            q.message,
            q.mode,
            q.filters_json,
            m.id as matter_id,
            m.title as matter_title,
            m.language,
            p.merkle_root,
            p.tx_hash,
            p.network,
            p.block_number
        FROM runs r
        JOIN queries q ON r.query_id = q.id
        JOIN matters m ON q.matter_id = m.id
        LEFT JOIN onchain_proofs p ON p.run_id = r.id
        WHERE r.id = :run_id
    """
    
    result = await db.execute(text(run_query), {"run_id": str(run_id)})
    run_row = result.fetchone()
    
    if not run_row:
        return None
    
    # Fetch agent votes for audit trail
    agent_votes_query = """
        SELECT 
            agent,
            decision_json,
            confidence,
            aligned,
            weights_before,
            weights_after
        FROM agent_votes
        WHERE run_id = :run_id
        ORDER BY agent
    """
    
    votes_result = await db.execute(text(agent_votes_query), {"run_id": str(run_id)})
    agent_votes = votes_result.fetchall()
    
    # Build comprehensive data structure
    run_data = {
        "run_id": str(run_row[0]),
        "answer": run_row[1],
        "confidence": float(run_row[2]) if run_row[2] else 0.0,
        "retrieval_set": run_row[3] or [],
        "created_at": run_row[4].isoformat() if run_row[4] else None,
        "query": {
            "id": str(run_row[5]),
            "message": run_row[6],
            "mode": run_row[7],
            "filters": run_row[8] or {}
        },
        "matter": {
            "id": str(run_row[9]),
            "title": run_row[10],
            "language": run_row[11]
        },
        "notarization": {
            "merkle_root": run_row[12],
            "tx_hash": run_row[13],
            "network": run_row[14],
            "block_number": run_row[15]
        } if run_row[12] else None,
        "agent_results": {
            vote[0]: {
                "reasoning": vote[1].get("reasoning", "") if vote[1] else "",
                "sources": vote[1].get("sources", []) if vote[1] else [],
                "confidence": float(vote[2]) if vote[2] else 0.0,
                "aligned": vote[3],
                "weights_before": vote[4] or {},
                "weights_after": vote[5] or {}
            }
            for vote in agent_votes
        },
        "citations": _extract_citations_from_retrieval(run_row[3] or []),
        "verification": {
            "confidence": float(run_row[2]) if run_row[2] else 0.0,
            "verification_level": _determine_verification_level(float(run_row[2]) if run_row[2] else 0.0)
        }
    }
    
    return run_data


def _extract_citations_from_retrieval(retrieval_set: list) -> list:
    """Extract citation information from retrieval set"""
    citations = []
    seen_authorities = set()
    
    for pack in retrieval_set:
        authority_id = pack.get("authority_id")
        if authority_id and authority_id not in seen_authorities:
            citations.append({
                "authority_id": authority_id,
                "title": pack.get("title", "Unknown Case"),
                "court": pack.get("court", "Unknown Court"),
                "neutral_cite": pack.get("neutral_cite", ""),
                "reporter_cite": pack.get("reporter_cite", ""),
                "para_ids": [p.get("para_id", 0) for p in pack.get("paras", [])]
            })
            seen_authorities.add(authority_id)
    
    return citations


def _determine_verification_level(confidence: float) -> str:
    """Determine verification level based on confidence score"""
    if confidence >= 0.8:
        return "high"
    elif confidence >= 0.6:
        return "medium"
    elif confidence >= 0.4:
        return "low"
    else:
        return "very_low"


async def _generate_export_file(run_data: Dict[str, Any], format: str, run_id: UUID) -> str:
    """Generate export file in requested format"""
    
    if format == "docx":
        return export_docx(str(run_id), run_data)
    elif format == "pdf":
        return export_pdf(str(run_id), run_data)
    elif format == "json":
        return write_audit_json(str(run_id), run_data)
    else:
        raise ValueError(f"Unsupported export format: {format}")


def _get_content_type(format: str) -> str:
    """Get MIME content type for export format"""
    content_types = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
        "json": "application/json"
    }
    return content_types.get(format, "application/octet-stream")


@router.get("/runs/{run_id}/export-cost")
async def get_export_cost(
    run_id: UUID,
    format: Literal["docx", "pdf", "json"],
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cost estimate for exporting a run without actually performing export
    """
    from app.billing.cost_calculator import CostCalculator
    
    try:
        # Fetch basic run data for cost calculation
        run_query = """
            SELECT r.retrieval_set_json, r.answer_text
            FROM runs r
            JOIN queries q ON r.query_id = q.id
            JOIN matters m ON q.matter_id = m.id
            WHERE r.id = :run_id
        """
        
        result = await db.execute(text(run_query), {"run_id": str(run_id)})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Run not found"
            )
        
        retrieval_set, answer_text = row
        run_data = {
            "retrieval_set": retrieval_set or [],
            "answer": answer_text or ""
        }
        
        calculator = CostCalculator()
        cost_breakdown = calculator.calculate_export_cost(format, run_data)
        
        return {
            "format": format,
            "estimated_cost_credits": cost_breakdown["total_credits"],
            "cost_breakdown": cost_breakdown,
            "user_balance": await _get_user_balance(db, user["id"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error("export.cost_estimate_error", 
                 run_id=str(run_id), 
                 format=format, 
                 error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate export cost"
        )


async def _get_user_balance(db: AsyncSession, user_id: str) -> int:
    """Get user's current credit balance"""
    result = await db.execute(
        text("SELECT credits_balance FROM billing_accounts WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    row = result.fetchone()
    return row[0] if row else 0


