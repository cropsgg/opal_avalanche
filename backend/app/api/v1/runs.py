from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.security import current_user
from app.db.session import get_db


router = APIRouter()


@router.get("/runs/{run_id}")
async def get_run(run_id: UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    row = (await db.execute(text("""
        select r.id, q.message, q.mode, r.answer_text, r.retrieval_set_json,
               p.merkle_root, p.tx_hash, p.network, p.block_number
        from runs r
        left join queries q on r.query_id=q.id
        left join onchain_proofs p on p.run_id=r.id
        where r.id=:rid
    """), {"rid": str(run_id)})).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return {
        "runId": str(row[0]),
        "message": row[1],
        "mode": row[2],
        "answer": row[3],
        "retrieval": row[4] or [],
        "notary": {"rootHash": row[5], "txHash": row[6], "network": row[7], "blockNumber": row[8]},
    }


