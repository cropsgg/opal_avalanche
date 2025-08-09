from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, Matter, Authority, Chunk
from app.db.models import Query, Run, OnchainProof, AgentVote
from app.db.models import User, Firm, UserFirm, BillingAccount


async def create_matter(db: AsyncSession, user_id: uuid.UUID, title: str, language: str = "en") -> Matter:
    matter = Matter(user_id=user_id, title=title, language=language)
    db.add(matter)
    await db.commit()
    await db.refresh(matter)
    return matter


async def get_matter(db: AsyncSession, matter_id: uuid.UUID) -> Optional[Matter]:
    res = await db.execute(select(Matter).where(Matter.id == matter_id))
    return res.scalar_one_or_none()


async def create_document(
    db: AsyncSession,
    matter_id: uuid.UUID,
    storage_path: str,
    filetype: str,
    size: Optional[int],
    uploaded_by: Optional[uuid.UUID],
) -> Document:
    doc = Document(
        matter_id=matter_id,
        storage_path=storage_path,
        filetype=filetype,
        size=size,
        uploaded_by=uploaded_by,
        ocr_status="pending",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def get_document(db: AsyncSession, doc_id: uuid.UUID) -> Optional[Document]:
    res = await db.execute(select(Document).where(Document.id == doc_id))
    return res.scalar_one_or_none()


async def create_query(
    db: AsyncSession,
    matter_id: uuid.UUID,
    message: str,
    mode: str,
    filters_json: dict,
) -> Query:
    q = Query(matter_id=matter_id, message=message, mode=mode, filters_json=filters_json)
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return q


async def create_run(
    db: AsyncSession,
    query_id: uuid.UUID,
    answer_text: str,
    confidence: float | None,
    retrieval_set_json: list,
) -> Run:
    r = Run(query_id=query_id, answer_text=answer_text, confidence=confidence, retrieval_set_json=retrieval_set_json)
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


async def save_onchain_proof(
    db: AsyncSession,
    run_id: uuid.UUID,
    merkle_root: str,
    tx_hash: str,
    network: str,
    block_number: int | None,
) -> OnchainProof:
    proof = OnchainProof(run_id=run_id, merkle_root=merkle_root, tx_hash=tx_hash, network=network, block_number=block_number)
    db.add(proof)
    await db.commit()
    await db.refresh(proof)
    return proof


# User Management CRUD Operations

async def create_user(db: AsyncSession, clerk_id: str, email: str, role: str = "lawyer", wallet_address: str | None = None) -> User:
    """Create a new user"""
    user = User(clerk_id=clerk_id, email=email, role=role, wallet_address=wallet_address)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_clerk_id(db: AsyncSession, clerk_id: str) -> Optional[User]:
    """Get user by Clerk ID"""
    result = await db.execute(select(User).where(User.clerk_id == clerk_id))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id: uuid.UUID, **kwargs) -> Optional[User]:
    """Update user fields"""
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """Soft delete user by marking as deleted (for compliance)"""
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    
    # Mark user as deleted rather than hard delete for audit purposes
    user.role = "deleted"
    user.email = f"deleted_{user.id}@deleted.local"
    
    await db.commit()
    return True


async def create_firm(db: AsyncSession, name: str, gstin: str | None = None, **kwargs) -> Firm:
    """Create a new firm"""
    firm = Firm(name=name, gstin=gstin, **kwargs)
    db.add(firm)
    await db.commit()
    await db.refresh(firm)
    return firm


async def get_firm_by_id(db: AsyncSession, firm_id: uuid.UUID) -> Optional[Firm]:
    """Get firm by ID"""
    result = await db.execute(select(Firm).where(Firm.id == firm_id))
    return result.scalar_one_or_none()


async def update_firm(db: AsyncSession, firm_id: uuid.UUID, **kwargs) -> Optional[Firm]:
    """Update firm fields"""
    firm = await get_firm_by_id(db, firm_id)
    if not firm:
        return None
    
    for key, value in kwargs.items():
        if hasattr(firm, key):
            setattr(firm, key, value)
    
    await db.commit()
    await db.refresh(firm)
    return firm


async def add_user_to_firm(db: AsyncSession, user_id: uuid.UUID, firm_id: uuid.UUID, role: str = "member") -> UserFirm:
    """Add user to firm with specified role"""
    user_firm = UserFirm(user_id=user_id, firm_id=firm_id, role=role)
    db.add(user_firm)
    await db.commit()
    await db.refresh(user_firm)
    return user_firm


async def remove_user_from_firm(db: AsyncSession, user_id: uuid.UUID, firm_id: uuid.UUID) -> bool:
    """Remove user from firm"""
    result = await db.execute(
        select(UserFirm).where(
            UserFirm.user_id == user_id,
            UserFirm.firm_id == firm_id
        )
    )
    user_firm = result.scalar_one_or_none()
    
    if not user_firm:
        return False
    
    await db.delete(user_firm)
    await db.commit()
    return True


async def get_user_firms(db: AsyncSession, user_id: uuid.UUID) -> List[dict]:
    """Get all firms for a user"""
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(UserFirm)
        .options(selectinload(UserFirm.firm))
        .where(UserFirm.user_id == user_id)
    )
    user_firms = result.scalars().all()
    
    return [
        {
            "firm_id": str(uf.firm_id),
            "firm_name": uf.firm.name,
            "role": uf.role,
            "joined_at": uf.joined_at,
            "firm_details": {
                "gstin": uf.firm.gstin,
                "pan": uf.firm.pan,
                "address": uf.firm.address,
                "city": uf.firm.city,
                "state": uf.firm.state,
                "email": uf.firm.email,
                "phone": uf.firm.phone
            }
        }
        for uf in user_firms
    ]


async def get_firm_users(db: AsyncSession, firm_id: uuid.UUID) -> List[dict]:
    """Get all users for a firm"""
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(UserFirm)
        .options(selectinload(UserFirm.user))
        .where(UserFirm.firm_id == firm_id)
    )
    user_firms = result.scalars().all()
    
    return [
        {
            "user_id": str(uf.user_id),
            "email": uf.user.email,
            "role_in_firm": uf.role,
            "user_role": uf.user.role,
            "joined_at": uf.joined_at,
            "wallet_address": uf.user.wallet_address
        }
        for uf in user_firms
        if uf.user.role != "deleted"  # Exclude deleted users
    ]


async def get_or_create_billing_account(db: AsyncSession, user_id: uuid.UUID) -> BillingAccount:
    """Get existing billing account or create new one for user"""
    result = await db.execute(select(BillingAccount).where(BillingAccount.user_id == user_id))
    billing_account = result.scalar_one_or_none()
    
    if billing_account:
        return billing_account
    
    # Create new billing account with free tier
    billing_account = BillingAccount(
        user_id=user_id,
        plan="free",
        credits_balance=100  # Free tier starts with 100 credits
    )
    db.add(billing_account)
    await db.commit()
    await db.refresh(billing_account)
    return billing_account


# Additional CRUD functions for ingestion pipeline

async def update_document_ocr_status(db: AsyncSession, doc_id: str, status: str) -> None:
    """Update document OCR status"""
    await db.execute(
        update(Document)
        .where(Document.id == uuid.UUID(doc_id))
        .values(ocr_status=status)
    )
    await db.commit()


async def create_authority(
    db: AsyncSession,
    court: str,
    title: str,
    neutral_cite: Optional[str] = None,
    reporter_cite: Optional[str] = None,
    date: Optional[datetime] = None,
    bench: Optional[str] = None,
    url: Optional[str] = None,
    metadata_json: Optional[dict] = None,
    storage_path: str = "",
    hash_keccak256: str = "",
) -> Authority:
    """Create new authority record"""
    authority = Authority(
        court=court,
        title=title,
        neutral_cite=neutral_cite,
        reporter_cite=reporter_cite,
        date=date,
        bench=bench,
        url=url,
        metadata_json=metadata_json or {},
        storage_path=storage_path,
        hash_keccak256=hash_keccak256,
    )
    db.add(authority)
    await db.commit()
    await db.refresh(authority)
    return authority


async def get_authority(db: AsyncSession, authority_id: uuid.UUID) -> Optional[Authority]:
    """Get authority by ID"""
    res = await db.execute(select(Authority).where(Authority.id == authority_id))
    return res.scalar_one_or_none()


async def create_chunk(
    db: AsyncSession,
    authority_id: uuid.UUID,
    para_from: Optional[int],
    para_to: Optional[int],
    text: str,
    tokens: Optional[int],
    vector_id: Optional[str],
    statute_tags: Optional[List[str]] = None,
    has_citation: bool = False,
) -> Chunk:
    """Create new chunk record"""
    chunk = Chunk(
        authority_id=authority_id,
        para_from=para_from,
        para_to=para_to,
        text=text,
        tokens=tokens,
        vector_id=vector_id,
        statute_tags=statute_tags or [],
        has_citation=has_citation,
    )
    db.add(chunk)
    await db.commit()
    await db.refresh(chunk)
    return chunk


async def get_chunks_by_authority(db: AsyncSession, authority_id: uuid.UUID) -> List[Chunk]:
    """Get all chunks for an authority"""
    res = await db.execute(select(Chunk).where(Chunk.authority_id == authority_id))
    return list(res.scalars().all())


async def create_agent_vote(
    db: AsyncSession,
    run_id: uuid.UUID,
    agent: str,
    decision_json: dict,
    confidence: float,
    aligned: Optional[bool] = None,
    weights_before: Optional[dict] = None,
    weights_after: Optional[dict] = None,
) -> AgentVote:
    """Create agent vote record"""
    vote = AgentVote(
        run_id=run_id,
        agent=agent,
        decision_json=decision_json,
        confidence=confidence,
        aligned=aligned,
        weights_before=weights_before,
        weights_after=weights_after,
    )
    db.add(vote)
    await db.commit()
    await db.refresh(vote)
    return vote


