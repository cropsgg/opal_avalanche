from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.core.security import current_user
from app.core.tasks import get_celery
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud
from app.storage.supabase_client import upload_bytes


router = APIRouter()


class DocumentCreateResponse(BaseModel):
    id: UUID
    ocr_status: str


@router.post("/matters/{matter_id}/documents", response_model=DocumentCreateResponse)
async def upload_document(
    matter_id: UUID,
    file: UploadFile = File(...),
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    # Upload to Supabase Storage
    data = await file.read()
    storage_path = f"matters/{matter_id}/{uuid4()}-{file.filename}"
    ok, err = upload_bytes(bucket="matters", path=storage_path, data=data, content_type=file.content_type or "application/octet-stream")
    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"upload failed: {err}")
    # Persist document row
    doc = await crud.create_document(
        db,
        matter_id=matter_id,
        storage_path=storage_path,
        filetype=file.content_type or "application/octet-stream",
        size=len(data),
        uploaded_by=UUID(user["id"]) if user.get("id") else None,
    )
    # Enqueue ingestion
    get_celery().send_task("app.ingestion.pipeline.ingest_document", args=[str(doc.id)])
    return DocumentCreateResponse(id=doc.id, ocr_status=doc.ocr_status)


