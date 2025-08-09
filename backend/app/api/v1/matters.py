from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import current_user
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud


router = APIRouter()


class MatterCreate(BaseModel):
    title: str
    language: str = "en"


class Matter(BaseModel):
    id: UUID
    title: str
    language: str


@router.post("/matters", response_model=Matter)
async def create_matter(req: MatterCreate, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    m = await crud.create_matter(db, user_id=UUID(user["id"]), title=req.title, language=req.language)
    return Matter(id=m.id, title=m.title, language=m.language)


@router.get("/matters/{matter_id}", response_model=Matter)
async def get_matter(matter_id: UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    m = await crud.get_matter(db, matter_id)
    if not m:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matter not found")
    return Matter(id=m.id, title=m.title, language=m.language)


