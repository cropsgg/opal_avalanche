from __future__ import annotations

import asyncio
from typing import Any, Dict, List
import structlog

from openai import OpenAI
from app.core.config import get_settings

log = structlog.get_logger()

# Legacy function
def rerank(query: str, packs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """MVP: identity ranking - legacy function"""
    return packs


async def rerank_chunks(query: str, chunks: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    """
    Re-rank chunks using LLM-based relevance scoring
    Returns chunks sorted by relevance with max coverage selection
    """
    
    if not chunks:
        return []
    
    if len(chunks) <= limit:
        return sorted(chunks, key=lambda x: x.get("normalized_score", 0), reverse=True)
    
    log.info("rerank.start", query_length=len(query), chunks_count=len(chunks), limit=limit)
    
    try:
        # Use LLM-based re-ranking for better relevance
        reranked = await _llm_rerank(query, chunks, limit * 2)  # Get more than needed for dedup
        
        # Apply max-coverage selection to diversify results
        final_chunks = _max_coverage_selection(reranked, limit)
        
        log.info("rerank.complete", 
                final_count=len(final_chunks),
                original_count=len(chunks))
        
        return final_chunks
        
    except Exception as e:
        log.error("rerank.error", error=str(e))
        # Fallback to score-based ranking
        return sorted(chunks, key=lambda x: x.get("normalized_score", 0), reverse=True)[:limit]


async def _llm_rerank(query: str, chunks: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    """Use OpenAI to score relevance of chunks to query"""
    
    settings = get_settings()
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Prepare chunks for scoring
    chunk_texts = []
    for i, chunk in enumerate(chunks):
        # Get text from chunk or from payload
        text = ""
        if "text" in chunk:
            text = chunk["text"][:500]  # Limit for API efficiency
        elif "payload" in chunk:
            # Construct text from payload
            payload = chunk["payload"]
            title = payload.get("title", "")
            neutral_cite = payload.get("neutral_cite", "")
            text = f"{title} {neutral_cite}"[:500]
        
        chunk_texts.append({
            "index": i,
            "text": text,
            "chunk": chunk
        })
    
    # Score chunks in batches
    scored_chunks = []
    batch_size = 10  # Reasonable batch size for API
    
    for i in range(0, len(chunk_texts), batch_size):
        batch = chunk_texts[i:i + batch_size]
        
        try:
            # Create relevance scoring prompt
            batch_scores = await _score_batch(client, query, batch)
            
            # Apply scores to chunks
            for j, score in enumerate(batch_scores):
                if i + j < len(chunks):
                    chunk_copy = chunks[i + j].copy()
                    chunk_copy["relevance_score"] = score
                    # Combine with original score
                    chunk_copy["final_score"] = (
                        0.3 * chunk_copy.get("normalized_score", 0) +
                        0.7 * score
                    )
                    scored_chunks.append(chunk_copy)
                    
        except Exception as e:
            log.warning("rerank.batch_error", batch_start=i, error=str(e))
            # Fallback: use original scores
            for j in range(len(batch)):
                if i + j < len(chunks):
                    chunk_copy = chunks[i + j].copy()
                    chunk_copy["final_score"] = chunk_copy.get("normalized_score", 0)
                    scored_chunks.append(chunk_copy)
    
    # Sort by final score
    scored_chunks.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    
    return scored_chunks[:limit]


async def _score_batch(client: OpenAI, query: str, batch: List[Dict[str, Any]]) -> List[float]:
    """Score a batch of chunks using LLM"""
    
    # Prepare scoring prompt
    chunk_summaries = []
    for item in batch:
        chunk_summaries.append(f"[{item['index']}] {item['text'][:200]}...")
    
    prompt = f"""Rate the relevance of each legal text chunk to the query on a scale of 0.0 to 1.0.

Query: {query}

Legal Text Chunks:
{chr(10).join(chunk_summaries)}

Return only a JSON array of scores in the same order, like: [0.8, 0.3, 0.9, ...]"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast model for scoring
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100
        )
        
        content = response.choices[0].message.content
        if not content:
            return [0.5] * len(batch)  # Neutral score fallback
            
        # Parse JSON scores
        import json
        scores = json.loads(content.strip())
        
        # Validate scores
        if isinstance(scores, list) and len(scores) == len(batch):
            # Clamp scores to 0-1 range
            return [max(0.0, min(1.0, float(s))) for s in scores]
        else:
            return [0.5] * len(batch)
            
    except Exception as e:
        log.warning("rerank.score_error", error=str(e))
        return [0.5] * len(batch)  # Neutral score fallback


def _max_coverage_selection(chunks: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    """
    Select chunks for maximum coverage while maintaining relevance
    Implements authority deduplication and domain diversity
    """
    
    if len(chunks) <= limit:
        return chunks
    
    selected = []
    seen_authorities = set()
    seen_courts = set()
    
    # First pass: select highest scoring chunk from each unique authority
    for chunk in chunks:
        auth_id = chunk.get("authority_id")
        if auth_id and auth_id not in seen_authorities:
            selected.append(chunk)
            seen_authorities.add(auth_id)
            
            # Track court diversity
            court = chunk.get("payload", {}).get("court")
            if court:
                seen_courts.add(court)
            
            if len(selected) >= limit:
                break
    
    # Second pass: fill remaining slots with court diversity preference
    if len(selected) < limit:
        remaining_chunks = [c for c in chunks if c.get("authority_id") not in seen_authorities]
        
        for chunk in remaining_chunks:
            court = chunk.get("payload", {}).get("court")
            
            # Prefer chunks from courts we haven't seen yet
            if court and court not in seen_courts:
                selected.append(chunk)
                seen_courts.add(court)
                if len(selected) >= limit:
                    break
        
        # Fill any remaining slots with highest scored chunks
        if len(selected) < limit:
            remaining = [c for c in remaining_chunks if c not in selected]
            selected.extend(remaining[:limit - len(selected)])
    
    return selected[:limit]


