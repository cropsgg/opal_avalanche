from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import current_user
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud
from app.notary.web3_client import publish_root as publish_onchain


router = APIRouter()


class NotarizeRequest(BaseModel):
    merkleRoot: str  # 0x-prefixed hex


@router.post("/runs/{run_id}/notarize")
async def notarize(run_id: UUID, req: NotarizeRequest, user=Depends(current_user), db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    receipt = publish_onchain(str(run_id), req.merkleRoot)
    await crud.save_onchain_proof(db, run_id=run_id, merkle_root=req.merkleRoot, tx_hash=receipt["transactionHash"], network="fuji", block_number=receipt.get("blockNumber"))
    return {"runId": str(run_id), "txHash": receipt["transactionHash"], "blockNumber": receipt.get("blockNumber")}


@router.get("/notary/{run_id}")
async def notary_get(run_id: UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    # Fetch stored proof
    # For brevity, use raw SQL SELECT to avoid adding more CRUD; in practice, model select
    from sqlalchemy import text

    row = (await db.execute(text("select merkle_root, tx_hash, network, block_number from onchain_proofs where run_id=:rid"), {"rid": str(run_id)})).first()
    if not row:
        return {"runId": str(run_id), "rootHash": None, "txHash": None}
    return {"runId": str(run_id), "rootHash": row[0], "txHash": row[1], "network": row[2], "blockNumber": row[3]}


