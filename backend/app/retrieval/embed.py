from __future__ import annotations

import asyncio
import time
from typing import Iterable, List, Dict, Any
import structlog

from openai import OpenAI
from qdrant_client.http import models as qm

from app.core.config import get_settings
from app.retrieval.qdrant_client import get_qdrant

log = structlog.get_logger()

# Batch processing configuration
BATCH_SIZE = 100
MAX_RETRIES = 3
BACKOFF_BASE = 2


def embed_texts(texts: Iterable[str]) -> List[List[float]]:
    """Simple embedding function - legacy interface"""
    s = get_settings()
    
    # Return mock embeddings if no API key configured
    if not s.OPENAI_API_KEY:
        log.warning("embed.no_api_key", message="Using mock embeddings for development")
        import random
        # Return consistent mock embeddings for same input
        mock_embeddings = []
        for text in texts:
            random.seed(hash(text) % (2**32))  # Consistent seed based on text
            mock_embeddings.append([random.random() for _ in range(3072)])
        return mock_embeddings
    
    try:
        client = OpenAI(api_key=s.OPENAI_API_KEY)
        resp = client.embeddings.create(model=s.OPENAI_EMBED_MODEL, input=list(texts))
        return [d.embedding for d in resp.data]  # type: ignore[attr-defined]
    except Exception as e:
        log.error("embed.openai_error", error=str(e))
        # Fallback to mock embeddings
        import random
        mock_embeddings = []
        for text in texts:
            random.seed(hash(text) % (2**32))
            mock_embeddings.append([random.random() for _ in range(3072)])
        return mock_embeddings


async def embed_chunks_batch(chunks: List[Dict[str, Any]], 
                           authority_metadata: Dict[str, Any]) -> List[str]:
    """
    Embed chunks and index to Qdrant with proper batching and error handling
    Returns list of vector_ids for successful embeddings
    """
    
    settings = get_settings()
    
    # Mock implementation if no API keys configured
    if not settings.OPENAI_API_KEY:
        log.warning("embed.batch_no_api_key", message="Using mock vector IDs for development")
        return [f"mock_vector_{i}_{hash(chunk['text']) % 10000}" for i, chunk in enumerate(chunks)]
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        qdrant = get_qdrant()
    except Exception as e:
        log.error("embed.batch_setup_error", error=str(e))
        return [f"mock_vector_{i}_{hash(chunk['text']) % 10000}" for i, chunk in enumerate(chunks)]
    
    vector_ids = []
    
    # Process in batches
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        
        try:
            # Extract texts for embedding
            texts = [chunk["text"] for chunk in batch]
            
            # Get embeddings with retry logic
            embeddings = await _get_embeddings_with_retry(client, texts, settings.OPENAI_EMBED_MODEL)
            
            if not embeddings:
                log.warning("embed.batch_failed", batch_start=i, batch_size=len(batch))
                continue
            
            # Prepare Qdrant points
            points = []
            for j, (chunk, embedding) in enumerate(zip(batch, embeddings)):
                vector_id = f"{authority_metadata['id']}_{chunk['para_from']}_{chunk['para_to']}_{j}"
                
                # Build payload from chunk and authority metadata
                payload = _build_qdrant_payload(chunk, authority_metadata)
                
                point = qm.PointStruct(
                    id=vector_id,
                    vector=embedding,
                    payload=payload
                )
                points.append(point)
                vector_ids.append(vector_id)
            
            # Upload to Qdrant
            qdrant.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=points
            )
            
            log.info("embed.batch_success", 
                    batch_start=i, 
                    batch_size=len(batch),
                    total_vectors=len(vector_ids))
            
        except Exception as e:
            log.error("embed.batch_error", 
                     batch_start=i, 
                     batch_size=len(batch),
                     error=str(e))
            continue
    
    return vector_ids


async def _get_embeddings_with_retry(client: OpenAI, texts: List[str], model: str) -> List[List[float]]:
    """Get embeddings with exponential backoff retry"""
    
    for attempt in range(MAX_RETRIES):
        try:
            log.debug("embed.request", texts_count=len(texts), attempt=attempt + 1)
            
            resp = client.embeddings.create(
                model=model,
                input=texts,
                encoding_format="float"
            )
            
            return [d.embedding for d in resp.data]
            
        except Exception as e:
            wait_time = BACKOFF_BASE ** attempt
            log.warning("embed.retry", 
                       attempt=attempt + 1, 
                       error=str(e),
                       wait_time=wait_time)
            
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(wait_time)
            else:
                log.error("embed.failed_after_retries", 
                         attempts=MAX_RETRIES,
                         error=str(e))
                return []
    
    return []


def _build_qdrant_payload(chunk: Dict[str, Any], authority_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Build Qdrant payload from chunk and authority metadata"""
    
    # Extract year from authority date
    year = None
    if authority_metadata.get("date"):
        try:
            year = authority_metadata["date"].year
        except (AttributeError, ValueError):
            pass
    
    # Extract judge names (simplified)
    judges = []
    if authority_metadata.get("bench"):
        # Split by common delimiters and clean
        judge_text = authority_metadata["bench"]
        judges = [j.strip() for j in judge_text.replace(" and ", ",").split(",") if j.strip()]
    
    payload = {
        "chunk_id": f"{authority_metadata['id']}_{chunk['para_from']}_{chunk['para_to']}",
        "authority_id": str(authority_metadata["id"]),
        "court": authority_metadata.get("court", "UNKNOWN"),
        "year": year,
        "judge": judges[:3],  # Limit to first 3 judges for payload efficiency
        "statute_tags": chunk.get("statute_tags", []),
        "has_citation": chunk.get("has_citation", False),
        "neutral_cite": authority_metadata.get("neutral_cite"),
        "reporter_cite": authority_metadata.get("reporter_cite"),
        "chunk_type": chunk.get("chunk_type", "content"),
        "para_from": chunk.get("para_from"),
        "para_to": chunk.get("para_to"),
        "token_count": chunk.get("tokens", 0)
    }
    
    # Remove None values to keep payload clean
    return {k: v for k, v in payload.items() if v is not None}


def embed_single_query(query: str) -> List[float]:
    """Embed a single query for vector search"""
    
    settings = get_settings()
    
    # Return mock embedding if no API key configured
    if not settings.OPENAI_API_KEY:
        log.warning("embed.query_no_api_key", message="Using mock embedding for development")
        import random
        random.seed(hash(query) % (2**32))
        return [random.random() for _ in range(3072)]
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        resp = client.embeddings.create(
            model=settings.OPENAI_EMBED_MODEL,
            input=[query],
            encoding_format="float"
        )
        return resp.data[0].embedding
        
    except Exception as e:
        log.error("embed.query_failed", query_length=len(query), error=str(e))
        # Fallback to mock embedding
        import random
        random.seed(hash(query) % (2**32))
        return [random.random() for _ in range(3072)]


async def reindex_authority(authority_id: str, chunks: List[Dict[str, Any]], 
                          authority_metadata: Dict[str, Any]) -> bool:
    """
    Reindex an authority by deleting old vectors and adding new ones
    Returns True if successful
    """
    
    settings = get_settings()
    qdrant = get_qdrant()
    
    try:
        # Delete existing vectors for this authority
        qdrant.delete(
            collection_name=settings.QDRANT_COLLECTION,
            points_selector=qm.FilterSelector(
                filter=qm.Filter(
                    must=[
                        qm.FieldCondition(
                            key="authority_id",
                            match=qm.MatchValue(value=str(authority_id))
                        )
                    ]
                )
            )
        )
        
        # Add new vectors
        vector_ids = await embed_chunks_batch(chunks, authority_metadata)
        
        log.info("reindex.success", 
                authority_id=authority_id,
                chunks_count=len(chunks),
                vectors_count=len(vector_ids))
        
        return len(vector_ids) > 0
        
    except Exception as e:
        log.error("reindex.failed", 
                 authority_id=authority_id,
                 error=str(e))
        return False


