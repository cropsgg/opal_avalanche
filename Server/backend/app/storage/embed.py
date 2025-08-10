"""
Embedding generation for text queries
"""
from __future__ import annotations

from typing import List
import structlog

from openai import OpenAI
from ..config.settings import get_settings

log = structlog.get_logger()


def embed_single_query(query: str) -> List[float]:
    """
    Generate embedding vector for a single query text
    
    Args:
        query: Text to embed
        
    Returns:
        List of embedding values (3072 dimensions for text-embedding-3-large)
    """
    settings = get_settings()
    
    if not settings.OPENAI_API_KEY:
        log.warning("embed.no_api_key", query_length=len(query))
        # Return zero vector as fallback
        return [0.0] * 3072
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.embeddings.create(
            input=query,
            model=settings.OPENAI_EMBED_MODEL
        )
        
        embedding = response.data[0].embedding
        
        log.debug("embed.success", 
                 query_length=len(query),
                 embedding_dim=len(embedding))
        
        return embedding
        
    except Exception as e:
        log.error("embed.failed", 
                 query_length=len(query),
                 error=str(e))
        
        # Return zero vector as fallback
        return [0.0] * 3072


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    settings = get_settings()
    
    if not settings.OPENAI_API_KEY:
        log.warning("embed.no_api_key", text_count=len(texts))
        return [[0.0] * 3072 for _ in texts]
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.embeddings.create(
            input=texts,
            model=settings.OPENAI_EMBED_MODEL
        )
        
        embeddings = [item.embedding for item in response.data]
        
        log.debug("embed.batch_success", 
                 text_count=len(texts),
                 embedding_count=len(embeddings))
        
        return embeddings
        
    except Exception as e:
        log.error("embed.batch_failed", 
                 text_count=len(texts),
                 error=str(e))
        
        # Return zero vectors as fallback
        return [[0.0] * 3072 for _ in texts]
