from __future__ import annotations

import json
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import structlog

from app.core.security import current_user
from app.db.session import get_db
from app.db import crud
from app.subnet.client import get_subnet_client
from app.subnet.encryption import seal_audit_data, get_subnet_encryption
from app.notary.merkle import merkle_root, para_hash

log = structlog.get_logger()

router = APIRouter()


class SubnetNotarizeRequest(BaseModel):
    """Request for subnet notarization - no merkle root needed, computed from run data"""
    include_audit_commit: bool = True  # Whether to also commit encrypted audit data


class SubnetNotarizeResponse(BaseModel):
    """Response from subnet notarization"""
    run_id: str
    merkle_root: str
    notary_tx_hash: str
    notary_block_number: int
    commit_tx_hash: str | None = None
    commit_block_number: int | None = None
    network: str = "subnet"


@router.post("/subnet/runs/{run_id}/notarize", response_model=SubnetNotarizeResponse)
async def subnet_notarize(
    run_id: UUID, 
    req: SubnetNotarizeRequest, 
    user=Depends(current_user), 
    db: AsyncSession = Depends(get_db)
) -> SubnetNotarizeResponse:
    """
    Notarize a research run on the private Avalanche subnet
    
    1. Fetches run data and computes Merkle root from evidence
    2. Publishes root to Notary contract on subnet
    3. Optionally encrypts and commits full audit data to CommitStore
    4. Stores proof in database
    """
    user_id = user["id"]
    
    log.info("subnet.notarize.start", 
             run_id=str(run_id), 
             user_id=user_id,
             include_audit=req.include_audit_commit)
    
    try:
        # Step 1: Fetch run data
        run_data = await _fetch_run_for_notarization(db, run_id, user_id)
        if not run_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Run not found or access denied"
            )
        
        # Step 2: Compute Merkle root from retrieval evidence
        merkle_root_hex = _compute_evidence_merkle_root(run_data)
        
        # Step 3: Publish to Notary contract
        subnet_client = get_subnet_client()
        notary_result = subnet_client.publish_notary(str(run_id), merkle_root_hex)
        
        # Step 4: Optionally commit encrypted audit data
        commit_result = None
        if req.include_audit_commit:
            audit_data = _build_audit_data(run_data)
            commit_result = await _commit_audit_data(str(run_id), audit_data)
        
        # Step 5: Save to database
        await crud.save_onchain_proof(
            db,
            run_id=run_id,
            merkle_root=merkle_root_hex,
            tx_hash=notary_result["transactionHash"],
            network="subnet",
            block_number=notary_result.get("blockNumber")
        )
        
        # If we also committed audit data, save that reference too
        if commit_result:
            await _save_audit_commit_ref(db, run_id, commit_result["transactionHash"])
        
        response = SubnetNotarizeResponse(
            run_id=str(run_id),
            merkle_root=merkle_root_hex,
            notary_tx_hash=notary_result["transactionHash"],
            notary_block_number=notary_result.get("blockNumber", 0),
            commit_tx_hash=commit_result["transactionHash"] if commit_result else None,
            commit_block_number=commit_result.get("blockNumber") if commit_result else None
        )
        
        log.info("subnet.notarize.success",
                run_id=str(run_id),
                merkle_root=merkle_root_hex,
                notary_tx=notary_result["transactionHash"],
                commit_tx=commit_result["transactionHash"] if commit_result else None)
        
        return response
        
    except Exception as e:
        log.error("subnet.notarize.failed", 
                 run_id=str(run_id), 
                 error=str(e), 
                 error_type=type(e).__name__)
        
        if isinstance(e, HTTPException):
            raise
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Notarization failed: {str(e)}"
        )


@router.get("/subnet/notary/{run_id}")
async def subnet_get_notarization(
    run_id: UUID, 
    user=Depends(current_user), 
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get notarization proof from subnet"""
    
    # Check database first
    row = (await db.execute(
        text("SELECT merkle_root, tx_hash, network, block_number FROM onchain_proofs WHERE run_id=:rid AND network='subnet'"),
        {"rid": str(run_id)}
    )).first()
    
    if not row:
        return {
            "run_id": str(run_id),
            "merkle_root": None,
            "tx_hash": None,
            "network": "subnet",
            "block_number": None,
            "verified": False
        }
    
    # Optionally verify against subnet (requires RPC access)
    verified = False
    try:
        subnet_client = get_subnet_client()
        subnet_root = subnet_client.get_notary(str(run_id))
        verified = (subnet_root is not None and subnet_root.lower() == row[0].lower())
    except Exception as e:
        log.warning("subnet.verify.failed", run_id=str(run_id), error=str(e))
    
    return {
        "run_id": str(run_id),
        "merkle_root": row[0],
        "tx_hash": row[1],
        "network": row[2],
        "block_number": row[3],
        "verified": verified
    }


@router.get("/subnet/audit/{run_id}")
async def subnet_get_audit_data(
    run_id: UUID,
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retrieve and decrypt audit data from subnet CommitStore
    This is for internal verification only - requires proper access
    """
    user_id = user["id"]
    
    try:
        # Verify user has access to this run
        run_check = (await db.execute(
            text("""
                SELECT r.id FROM runs r
                JOIN queries q ON r.query_id = q.id  
                JOIN matters m ON q.matter_id = m.id
                WHERE r.id = :rid AND m.user_id = :uid
            """),
            {"rid": str(run_id), "uid": user_id}
        )).first()
        
        if not run_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Run not found or access denied"
            )
        
        # Get encrypted data from subnet
        subnet_client = get_subnet_client()
        ciphertext = subnet_client.get_commit(str(run_id))
        
        if not ciphertext:
            return {
                "run_id": str(run_id),
                "audit_data": None,
                "encrypted": True,
                "available": False
            }
        
        # Decrypt audit data
        encryption = get_subnet_encryption()
        audit_data = encryption.unseal_json(ciphertext, "run-audit-v1")
        
        return {
            "run_id": str(run_id),
            "audit_data": audit_data,
            "encrypted": True,
            "available": True,
            "ciphertext_size": len(ciphertext)
        }
        
    except Exception as e:
        log.error("subnet.audit.decrypt_failed", run_id=str(run_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit data"
        )


# Helper functions

async def _fetch_run_for_notarization(
    db: AsyncSession, 
    run_id: UUID, 
    user_id: str
) -> Dict[str, Any] | None:
    """Fetch run data with access control"""
    
    row = (await db.execute(
        text("""
            SELECT r.id, r.answer_text, r.confidence, r.retrieval_set_json,
                   q.message, q.mode, q.filters_json,
                   m.title, m.language
            FROM runs r
            JOIN queries q ON r.query_id = q.id
            JOIN matters m ON q.matter_id = m.id  
            WHERE r.id = :rid AND m.user_id = :uid
        """),
        {"rid": str(run_id), "uid": user_id}
    )).first()
    
    if not row:
        return None
    
    # Also get agent votes if available
    votes_result = await db.execute(
        text("SELECT agent, decision_json, confidence, aligned FROM agent_votes WHERE run_id = :rid"),
        {"rid": str(run_id)}
    )
    votes = [
        {
            "agent": vote[0],
            "decision": vote[1],
            "confidence": vote[2],
            "aligned": vote[3]
        }
        for vote in votes_result.fetchall()
    ]
    
    return {
        "run_id": str(row[0]),
        "answer_text": row[1],
        "confidence": row[2],
        "retrieval_set": row[3] or [],
        "query": {
            "message": row[4],
            "mode": row[5],
            "filters": row[6] or {}
        },
        "matter": {
            "title": row[7],
            "language": row[8]
        },
        "agent_votes": votes
    }


def _compute_evidence_merkle_root(run_data: Dict[str, Any]) -> str:
    """Compute Merkle root from retrieval evidence"""
    
    retrieval_set = run_data.get("retrieval_set", [])
    
    if not retrieval_set:
        # No evidence - return zero hash
        return "0x" + "00" * 32
    
    # Extract text from retrieval evidence and hash each paragraph
    hashes = []
    for item in retrieval_set:
        if isinstance(item, dict) and "text" in item:
            text = item["text"]
            if text and text.strip():
                hashes.append(para_hash(text.strip()))
    
    if not hashes:
        return "0x" + "00" * 32
    
    # Compute Merkle root
    root = merkle_root(hashes)
    return "0x" + root.hex()


def _build_audit_data(run_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build comprehensive audit data for encryption"""
    
    return {
        "version": "opal-audit-v1",
        "run_id": run_data["run_id"],
        "timestamp": run_data.get("created_at"),
        "query": run_data["query"],
        "matter": run_data["matter"],
        "answer": {
            "text": run_data["answer_text"],
            "confidence": run_data.get("confidence")
        },
        "evidence": {
            "retrieval_set": run_data["retrieval_set"],
            "evidence_count": len(run_data.get("retrieval_set", []))
        },
        "agent_analysis": {
            "votes": run_data.get("agent_votes", []),
            "vote_count": len(run_data.get("agent_votes", []))
        },
        "integrity": {
            "merkle_root": _compute_evidence_merkle_root(run_data),
            "evidence_hash": get_subnet_encryption().data_hash(
                json.dumps(run_data["retrieval_set"], sort_keys=True).encode()
            ).hex()
        }
    }


async def _commit_audit_data(commit_id: str, audit_data: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypt and commit audit data to subnet"""
    
    # Encrypt audit data
    ciphertext, label_hash, data_hash = seal_audit_data(audit_data)
    
    # Commit to subnet
    subnet_client = get_subnet_client()
    return subnet_client.commit_blob(commit_id, label_hash, ciphertext, data_hash)


async def _save_audit_commit_ref(db: AsyncSession, run_id: UUID, commit_tx_hash: str):
    """Save reference to audit commit transaction"""
    # For now, we could extend the onchain_proofs table or create a separate table
    # This is a placeholder for tracking the commit transaction
    pass
