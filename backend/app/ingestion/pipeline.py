from __future__ import annotations

import asyncio
from pathlib import Path
import structlog
from typing import Dict, Any, List

from app.core.tasks import get_celery
from app.db.session import get_db
from app.db import crud
import uuid
from app.storage.supabase_client import download_bytes
from app.ingestion.ocr import has_text_layer, ocr_pdf_pages
from app.ingestion.parse_pdf import extract_text_with_paras as parse_pdf_paras, has_text_layer as pdf_has_text
from app.ingestion.parse_docx import extract_text_with_paras as parse_docx_paras
from app.ingestion.normalize import extract_metadata, compute_document_hash
from app.retrieval.chunking import create_chunks
from app.retrieval.embed import embed_chunks_batch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

log = structlog.get_logger()


@get_celery().task(name="app.ingestion.pipeline.ingest_document")
def ingest_document(doc_id: str) -> str:
    """
    Complete document ingestion pipeline
    Async wrapper for the main ingestion logic
    """
    try:
        result = asyncio.run(_ingest_document_async(doc_id))
        return result
    except Exception as e:
        log.error("ingest.pipeline_error", doc_id=doc_id, error=str(e))
        return f"error: {str(e)}"


async def _ingest_document_async(doc_id: str) -> str:
    """Main ingestion pipeline implementation"""
    
    log.info("ingest.start", doc_id=doc_id)
    
    # Get database session
    async for db in get_db():
        try:
            # 1. Fetch document metadata
            try:
                doc_uuid = uuid.UUID(doc_id)
            except Exception:
                raise ValueError(f"Invalid document id: {doc_id}")
            doc = await crud.get_document(db, doc_uuid)
            if not doc:
                raise ValueError(f"Document {doc_id} not found")
            
            log.info("ingest.document_found", 
                    doc_id=doc_id, 
                    filetype=doc.filetype,
                    storage_path=doc.storage_path)
            
            # 2. Download from storage
            data, error = download_bytes("matters", doc.storage_path)
            if error:
                raise ValueError(f"Failed to download: {error}")
            
            # 3. Update status to processing
            await crud.update_document_ocr_status(db, doc_id, "processing")
            
            # 4. Extract/OCR text and parse paragraphs
            paragraphs = await _extract_and_parse(data, doc.filetype, doc.storage_path)
            
            if not paragraphs:
                await crud.update_document_ocr_status(db, doc_id, "failed_no_text")
                return "failed: no text extracted"
            
            log.info("ingest.text_extracted", 
                    doc_id=doc_id, 
                    paragraphs_count=len(paragraphs))
            
            # 5. Extract metadata and create authority record
            full_text = " ".join([p.get("text", "") for p in paragraphs])
            metadata = extract_metadata(full_text, paragraphs)
            document_hash = compute_document_hash(full_text)
            
            # Create authority record
            authority = await crud.create_authority(
                db,
                court=metadata.get("court", "UNKNOWN"),
                title=metadata.get("title", f"Document {doc_id}"),
                neutral_cite=metadata.get("neutral_cite"),
                reporter_cite=metadata.get("reporter_cite"),
                date=metadata.get("date"),
                bench=metadata.get("bench"),
                url=None,
                metadata_json=metadata,
                storage_path=doc.storage_path,
                hash_keccak256=document_hash
            )
            
            log.info("ingest.authority_created", 
                    doc_id=doc_id,
                    authority_id=str(authority.id),
                    court=metadata.get("court"))
            
            # 6. Create chunks
            chunks = create_chunks(paragraphs, str(authority.id))
            
            if not chunks:
                await crud.update_document_ocr_status(db, doc_id, "failed_no_chunks")
                return "failed: no chunks created"
            
            log.info("ingest.chunks_created", 
                    doc_id=doc_id,
                    chunks_count=len(chunks))
            
            # 7. Embed and index chunks
            authority_metadata = {
                "id": authority.id,
                "court": authority.court,
                "title": authority.title,
                "neutral_cite": authority.neutral_cite,
                "reporter_cite": authority.reporter_cite,
                "date": authority.date,
                "bench": authority.bench
            }
            
            vector_ids = await embed_chunks_batch(chunks, authority_metadata)
            
            if not vector_ids:
                await crud.update_document_ocr_status(db, doc_id, "failed_embedding")
                return "failed: embedding failed"
            
            # 8. Store chunks in database with vector_ids
            chunk_records = []
            for i, (chunk, vector_id) in enumerate(zip(chunks, vector_ids)):
                chunk_record = await crud.create_chunk(
                    db,
                    authority_id=authority.id,
                    para_from=chunk.get("para_from"),
                    para_to=chunk.get("para_to"),
                    text=chunk["text"],
                    tokens=chunk.get("tokens"),
                    vector_id=vector_id,
                    statute_tags=chunk.get("statute_tags", []),
                    has_citation=chunk.get("has_citation", False)
                )
                chunk_records.append(chunk_record)
            
            # 9. Update FTS index
            await _update_fts_index(db, authority)
            
            # 10. Update document status to completed
            await crud.update_document_ocr_status(db, doc_id, "completed")
            
            log.info("ingest.complete", 
                    doc_id=doc_id,
                    authority_id=str(authority.id),
                    chunks_stored=len(chunk_records),
                    vectors_indexed=len(vector_ids))
            
            return f"success: {len(chunk_records)} chunks processed"
            
        except Exception as e:
            await crud.update_document_ocr_status(db, doc_id, f"failed: {str(e)[:100]}")
            log.error("ingest.error", doc_id=doc_id, error=str(e))
            raise
        finally:
            await db.close()


async def _extract_and_parse(data: bytes, filetype: str, storage_path: str) -> List[Dict[str, Any]]:
    """Extract text and parse into paragraphs based on file type"""
    
    file_ext = Path(storage_path).suffix.lower()
    
    try:
        if file_ext == '.pdf' or 'pdf' in filetype.lower():
            # Check if PDF has text layer
            if pdf_has_text(data):
                log.info("ingest.pdf_text_layer", storage_path=storage_path)
                return parse_pdf_paras(data)
            else:
                log.info("ingest.pdf_ocr_needed", storage_path=storage_path)
                # TODO: Implement OCR pipeline for scanned PDFs
                # For now, try text extraction anyway
                return parse_pdf_paras(data)
                
        elif file_ext in ['.docx', '.doc'] or 'word' in filetype.lower():
            log.info("ingest.docx_parsing", storage_path=storage_path)
            return parse_docx_paras(data)
            
        else:
            log.warning("ingest.unsupported_filetype", 
                       filetype=filetype, 
                       storage_path=storage_path)
            return []
            
    except Exception as e:
        log.error("ingest.parse_error", 
                 filetype=filetype,
                 storage_path=storage_path,
                 error=str(e))
        return []


async def _update_fts_index(db: AsyncSession, authority) -> None:
    """Update full-text search index for the authority"""
    
    try:
        # Build FTS document from title and metadata
        title = authority.title or ""
        headnote = authority.metadata_json.get("headnote", "") if authority.metadata_json else ""
        
        # Update FTS column
        await db.execute(
            text("""
                UPDATE authorities 
                SET fts_doc = 
                    setweight(to_tsvector('simple', :title), 'A') ||
                    setweight(to_tsvector('english', :headnote), 'B')
                WHERE id = :authority_id
            """),
            {
                "title": title,
                "headnote": headnote,
                "authority_id": str(authority.id)
            }
        )
        
        await db.commit()
        
        log.info("ingest.fts_updated", authority_id=str(authority.id))
        
    except Exception as e:
        log.error("ingest.fts_error", 
                 authority_id=str(authority.id),
                 error=str(e))
        # Don't fail the whole pipeline for FTS errors
        await db.rollback()


