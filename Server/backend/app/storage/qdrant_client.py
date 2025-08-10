from __future__ import annotations

from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
import structlog

from ..config.settings import get_settings

log = structlog.get_logger()


def get_qdrant() -> QdrantClient:
    """Get Qdrant client instance"""
    s = get_settings()
    try:
        return QdrantClient(url=s.QDRANT_URL, api_key=s.QDRANT_API_KEY)
    except Exception as e:
        log.warning("qdrant.connection_failed", error=str(e), url=s.QDRANT_URL)
        raise RuntimeError(f"Qdrant connection failed: {e}")


def ensure_collection() -> None:
    """Ensure the collection exists"""
    s = get_settings()
    try:
        client = get_qdrant()
        if s.QDRANT_COLLECTION in [c.name for c in client.get_collections().collections]:
            return
    except Exception as e:
        log.warning("qdrant.ensure_collection_skipped", error=str(e))
        return
    
    client.create_collection(
        collection_name=s.QDRANT_COLLECTION,
        vectors=qm.VectorParams(size=3072, distance=qm.Distance.COSINE),
        hnsw_config=qm.HnswConfigDiff(m=32, ef_construct=128),
        optimizers_config=qm.OptimizersConfigDiff(memmap_threshold=200_000_000),
        quantization_config=qm.ScalarQuantization(
            scalar=qm.ScalarQuantizationConfig(type="int8", always_ram=False)
        ),
    )
    
    # Create payload indexes
    for field, ftype in [
        ("court", qm.PayloadSchemaType.KEYWORD),
        ("year", qm.PayloadSchemaType.INTEGER),
        ("has_citation", qm.PayloadSchemaType.BOOL),
        ("statute_tags", qm.PayloadSchemaType.KEYWORD),
    ]:
        client.create_payload_index(
            s.QDRANT_COLLECTION, 
            field_name=field, 
            field_schema=qm.PayloadSchemaType(ftype)
        )


def search(
    query_vector: List[float], 
    filters: Optional[Dict[str, Any]] = None, 
    top_k: int = 24
) -> List[qm.ScoredPoint]:
    """Search vectors in Qdrant"""
    s = get_settings()
    try:
        client = get_qdrant()
        qfilter = None
        
        if filters:
            must = []
            for k, v in filters.items():
                if isinstance(v, list):
                    must.append(qm.FieldCondition(key=k, match=qm.MatchAny(any=v)))
                else:
                    must.append(qm.FieldCondition(key=k, match=qm.MatchValue(value=v)))
            qfilter = qm.Filter(must=must)
        
        return client.search(
            collection_name=s.QDRANT_COLLECTION, 
            query_vector=query_vector, 
            limit=top_k, 
            query_filter=qfilter
        )
    except Exception as e:
        log.warning("qdrant.search_failed", error=str(e))
        return []


def get_collection_info() -> Dict[str, Any]:
    """Get collection information"""
    s = get_settings()
    try:
        client = get_qdrant()
        collection_info = client.get_collection(s.QDRANT_COLLECTION)
        return {
            "name": collection_info.config.collection_name,
            "vectors_count": collection_info.vectors_count,
            "indexed_vectors_count": collection_info.indexed_vectors_count,
            "points_count": collection_info.points_count,
            "status": collection_info.status,
        }
    except Exception as e:
        log.warning("qdrant.collection_info_failed", error=str(e))
        return {"error": str(e)}


def health_check() -> Dict[str, Any]:
    """Check Qdrant health"""
    try:
        client = get_qdrant()
        # Simple ping-like operation
        collections = client.get_collections()
        return {
            "status": "healthy",
            "collections_count": len(collections.collections),
            "available": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "available": False
        }