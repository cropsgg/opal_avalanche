from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.fts import fts_search, trigram_cite_search
from app.retrieval.qdrant_client import search as qdrant_search
from app.retrieval.embed import embed_single_query
from app.retrieval.rerank import rerank_chunks
from app.retrieval.filters import build_qdrant_filters, validate_filters

log = structlog.get_logger()


async def retrieve_packs(db: AsyncSession, query: str, limit: int = 12, 
                        filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Hybrid retrieval combining vector search, FTS, and re-ranking
    Returns top chunks with authority metadata and deduplication
    """
    
    log.info("retrieval.start", query_length=len(query), limit=limit)
    
    # Validate and build filters
    validated_filters = validate_filters(filters or {})
    qdrant_filters = build_qdrant_filters(validated_filters)
    
    # Parallel retrieval from multiple sources
    vector_results = await _get_vector_results(query, qdrant_filters, limit * 2)
    fts_results = await _get_fts_results(db, query, limit * 2)
    
    # Check for citation queries and use trigram search
    citation_results = []
    if _is_citation_query(query):
        citation_results = await trigram_cite_search(db, query, limit)
    
    # Combine and deduplicate results
    combined_chunks = _combine_results(vector_results, fts_results, citation_results)
    
    if not combined_chunks:
        log.warning("retrieval.no_results", query=query)
        return []
    
    # Re-rank using cross-encoder or LLM
    reranked_chunks = await rerank_chunks(query, combined_chunks, limit)
    
    # Pack results with authority metadata and deduplication
    final_packs = await _pack_results(db, reranked_chunks, limit)
    
    log.info("retrieval.complete", 
            query=query,
            vector_count=len(vector_results),
            fts_count=len(fts_results),
            final_count=len(final_packs))
    
    return final_packs


async def _get_vector_results(query: str, filters: Optional[Dict[str, Any]], 
                            limit: int) -> List[Dict[str, Any]]:
    """Get results from Qdrant vector search"""
    
    try:
        # Embed query
        query_vector = embed_single_query(query)
        if not query_vector:
            log.warning("retrieval.embed_failed", query=query)
            return []
        
        # Search Qdrant
        qdrant_results = qdrant_search(query_vector, filters, top_k=limit)
        
        # Convert to standard format
        vector_results = []
        for point in qdrant_results:
            vector_results.append({
                "chunk_id": point.payload.get("chunk_id"),
                "authority_id": point.payload.get("authority_id"),
                "score": point.score,
                "source": "vector",
                "payload": dict(point.payload),
                "para_from": point.payload.get("para_from"),
                "para_to": point.payload.get("para_to"),
            })
        
        return vector_results
        
    except Exception as e:
        log.error("retrieval.vector_error", query=query, error=str(e))
        return []


async def _get_fts_results(db: AsyncSession, query: str, limit: int) -> List[Dict[str, Any]]:
    """Get results from PostgreSQL full-text search"""
    
    try:
        fts_authorities = await fts_search(db, query, limit=limit)
        
        # Convert to chunk format for consistency
        fts_results = []
        for auth in fts_authorities:
            fts_results.append({
                "chunk_id": f"fts_{auth['id']}",
                "authority_id": str(auth["id"]),
                "score": float(auth.get("rank", 0.0)),
                "source": "fts",
                "payload": {
                    "title": auth.get("title"),
                    "neutral_cite": auth.get("neutral_cite"),
                    "reporter_cite": auth.get("reporter_cite"),
                },
                "para_from": None,
                "para_to": None,
            })
        
        return fts_results
        
    except Exception as e:
        log.error("retrieval.fts_error", query=query, error=str(e))
        return []


def _is_citation_query(query: str) -> bool:
    """Detect if query contains legal citations"""
    citation_patterns = [
        r"\d{4}\s+\d+\s+SCC\s+\d+",
        r"AIR\s+\d{4}",
        r"\(\d{4}\)\s+\d+\s+SCC",
        r"v\.|vs\.",
        r"[A-Z][a-z]+\s+v\.?\s+[A-Z][a-z]+",
    ]
    
    import re
    for pattern in citation_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False


def _combine_results(vector_results: List[Dict[str, Any]], 
                    fts_results: List[Dict[str, Any]], 
                    citation_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Combine results from different sources with score normalization"""
    
    all_results = []
    
    # Normalize vector scores (0-1 range)
    if vector_results:
        max_vector_score = max(r["score"] for r in vector_results)
        for result in vector_results:
            result["normalized_score"] = result["score"] / max_vector_score if max_vector_score > 0 else 0
            all_results.append(result)
    
    # Normalize FTS scores (ts_rank is typically 0-1)
    for result in fts_results:
        result["normalized_score"] = min(result["score"], 1.0)
        all_results.append(result)
    
    # Citation results get boosted scores
    for result in citation_results:
        result["normalized_score"] = 0.9  # High relevance for citation matches
        result["source"] = "citation"
        all_results.append(result)
    
    # Remove duplicates by authority_id, keeping highest scoring
    seen_authorities = {}
    for result in all_results:
        auth_id = result["authority_id"]
        if auth_id not in seen_authorities or result["normalized_score"] > seen_authorities[auth_id]["normalized_score"]:
            seen_authorities[auth_id] = result
    
    return list(seen_authorities.values())


async def _pack_results(db: AsyncSession, chunks: List[Dict[str, Any]], 
                       limit: int) -> List[Dict[str, Any]]:
    """Pack chunks into final format with authority metadata"""
    
    from sqlalchemy import text
    
    # Get authority metadata for all chunks
    authority_ids = [c["authority_id"] for c in chunks]
    if not authority_ids:
        return []
    
    # Fetch authority metadata
    placeholders = ",".join([f"'{aid}'" for aid in authority_ids])
    query = f"""
        SELECT id, court, title, neutral_cite, reporter_cite, date, bench, url
        FROM authorities 
        WHERE id::text IN ({placeholders})
    """
    
    result = await db.execute(text(query))
    authorities = {str(row[0]): dict(row._mapping) for row in result.fetchall()}
    
    # Build final packs
    packs = []
    for chunk in chunks[:limit]:
        auth_id = chunk["authority_id"]
        authority = authorities.get(auth_id, {})
        
        # Get paragraph information if available
        paras = []
        if chunk.get("para_from") and chunk.get("para_to"):
            paras = [{
                "para_id": chunk["para_from"],
                "para_to": chunk["para_to"],
                "text": "",  # Will be loaded separately if needed
                "score": chunk.get("normalized_score", 0.0)
            }]
        
        pack = {
            "authority_id": auth_id,
            "title": authority.get("title", "Unknown"),
            "court": authority.get("court", "UNKNOWN"),
            "neutral_cite": authority.get("neutral_cite"),
            "reporter_cite": authority.get("reporter_cite"),
            "date": authority.get("date"),
            "bench": authority.get("bench"),
            "url": authority.get("url"),
            "paras": paras,
            "score": chunk.get("normalized_score", 0.0),
            "source": chunk.get("source", "unknown"),
            "metadata": chunk.get("payload", {})
        }
        
        packs.append(pack)
    
    return packs


# Legacy function for backwards compatibility
async def retrieve_packs_simple(db: AsyncSession, query: str, limit: int = 12) -> List[Dict[str, Any]]:
    """Simple retrieval using FTS only - for backwards compatibility"""
    results = await fts_search(db, query, limit=limit)
    packs: List[Dict[str, Any]] = []
    for r in results:
        packs.append({
            "authority_id": r["id"],
            "title": r.get("title"),
            "neutral_cite": r.get("neutral_cite"),
            "reporter_cite": r.get("reporter_cite"),
            "paras": [],
        })
    return packs


