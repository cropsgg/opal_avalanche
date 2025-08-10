"""
Knowledge Graph API endpoints for OPAL Server
Provides endpoints to visualize and interact with the knowledge graph stored in Qdrant
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import asyncio
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
import numpy as np
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import networkx as nx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knowledge-graph", tags=["Knowledge Graph"])

# Pydantic models for request/response
class GraphNode(BaseModel):
    id: str
    label: str
    content: str
    metadata: Dict[str, Any]
    position: Dict[str, float]  # x, y coordinates
    cluster: int
    size: float  # Node size based on connections or importance
    color: str   # Color based on cluster or type

class GraphEdge(BaseModel):
    source: str
    target: str
    weight: float
    label: Optional[str] = None

class KnowledgeGraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    clusters: Dict[str, Any]
    metadata: Dict[str, Any]

class GraphFilterRequest(BaseModel):
    search_query: Optional[str] = None
    cluster_id: Optional[int] = None
    limit: int = 100
    min_similarity: float = 0.7

# Color palette for clusters
CLUSTER_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57",
    "#FF9FF3", "#54A0FF", "#5F27CD", "#00D2D3", "#FF9F43",
    "#1DD1A1", "#C44569", "#F8B500", "#7159C1", "#3742FA"
]

def get_qdrant_client():
    """Get Qdrant client instance"""
    try:
        return QdrantClient(url="http://qdrant:6333")
    except Exception:
        # Fallback to localhost for development
        return QdrantClient(url="http://localhost:6333")

def compute_similarity_edges(vectors: List[List[float]], threshold: float = 0.7) -> List[Dict[str, Any]]:
    """Compute edges based on vector similarity"""
    edges = []
    vectors_array = np.array(vectors)
    
    # Compute cosine similarity matrix
    norms = np.linalg.norm(vectors_array, axis=1)
    similarity_matrix = np.dot(vectors_array, vectors_array.T) / np.outer(norms, norms)
    
    # Create edges for similar vectors above threshold
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            similarity = similarity_matrix[i][j]
            if similarity > threshold:
                edges.append({
                    "source": str(i),
                    "target": str(j),
                    "weight": float(similarity),
                    "label": f"{similarity:.2f}"
                })
    
    return edges

def compute_graph_layout(vectors: List[List[float]]) -> List[Dict[str, float]]:
    """Compute 2D positions for graph nodes using t-SNE"""
    if len(vectors) < 2:
        return [{"x": 0, "y": 0} for _ in vectors]
    
    vectors_array = np.array(vectors)
    
    # Use t-SNE for dimensionality reduction to 2D
    perplexity = min(30, len(vectors) - 1)
    if perplexity < 1:
        perplexity = 1
        
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
    positions_2d = tsne.fit_transform(vectors_array)
    
    # Normalize positions to [0, 1000] range for better visualization
    min_vals = positions_2d.min(axis=0)
    max_vals = positions_2d.max(axis=0)
    ranges = max_vals - min_vals
    ranges[ranges == 0] = 1  # Avoid division by zero
    
    normalized_positions = (positions_2d - min_vals) / ranges * 1000
    
    return [{"x": float(pos[0]), "y": float(pos[1])} for pos in normalized_positions]

def compute_clusters(vectors: List[List[float]], n_clusters: int = 8) -> List[int]:
    """Compute clusters using K-means"""
    if len(vectors) < n_clusters:
        return list(range(len(vectors)))
    
    vectors_array = np.array(vectors)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(vectors_array)
    
    return cluster_labels.tolist()

@router.get("/", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of nodes to return"),
    min_similarity: float = Query(0.7, ge=0.1, le=1.0, description="Minimum similarity for edges"),
    search_query: Optional[str] = Query(None, description="Search query to filter nodes"),
    cluster_count: int = Query(8, ge=2, le=15, description="Number of clusters to create")
):
    """
    Get knowledge graph data from Opal_db_1000 collection
    """
    try:
        client = get_qdrant_client()
        
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if "Opal_db_1000" not in collection_names:
            raise HTTPException(
                status_code=404, 
                detail="Collection 'Opal_db_1000' not found. Available collections: " + ", ".join(collection_names)
            )
        
        # Get collection info
        collection_info = client.get_collection("Opal_db_1000")
        
        # Search or scroll through the collection
        if search_query:
            # Perform semantic search if query provided
            # Note: This requires having an embedding model to encode the query
            # For now, we'll use scroll with payload filtering
            points = client.scroll(
                collection_name="Opal_db_1000",
                limit=limit,
                with_payload=True,
                with_vectors=True
            )[0]  # Get the points from the tuple
        else:
            # Scroll through all points
            points = client.scroll(
                collection_name="Opal_db_1000",
                limit=limit,
                with_payload=True,
                with_vectors=True
            )[0]  # Get the points from the tuple
        
        if not points:
            return KnowledgeGraphResponse(
                nodes=[],
                edges=[],
                clusters={},
                metadata={"total_points": 0, "collection_info": collection_info.dict()}
            )
        
        # Extract vectors and metadata
        vectors = []
        node_data = []
        
        for point in points:
            vectors.append(point.vector)
            payload = point.payload or {}
            
            node_data.append({
                "id": str(point.id),
                "content": payload.get("text", ""),
                "metadata": payload
            })
        
        # Compute graph layout using t-SNE
        positions = compute_graph_layout(vectors)
        
        # Compute clusters
        cluster_labels = compute_clusters(vectors, cluster_count)
        
        # Compute similarity edges
        edges_data = compute_similarity_edges(vectors, min_similarity)
        
        # Create graph for network analysis
        G = nx.Graph()
        for edge in edges_data:
            G.add_edge(edge["source"], edge["target"], weight=edge["weight"])
        
        # Compute node sizes based on degree centrality
        centrality = nx.degree_centrality(G) if G.nodes() else {}
        
        # Create nodes
        nodes = []
        for i, (data, position, cluster) in enumerate(zip(node_data, positions, cluster_labels)):
            node_id = data["id"]
            centrality_score = centrality.get(str(i), 0)
            
            # Determine node size based on centrality (20-80 range)
            size = 20 + (centrality_score * 60)
            
            # Get cluster color
            color = CLUSTER_COLORS[cluster % len(CLUSTER_COLORS)]
            
            # Create node label from content
            content = data["content"]
            label = content[:50] + "..." if len(content) > 50 else content
            if not label.strip():
                label = f"Node {i + 1}"
            
            nodes.append(GraphNode(
                id=node_id,
                label=label,
                content=content,
                metadata=data["metadata"],
                position=position,
                cluster=cluster,
                size=size,
                color=color
            ))
        
        # Create edges with correct node IDs
        edges = []
        for edge_data in edges_data:
            source_idx = int(edge_data["source"])
            target_idx = int(edge_data["target"])
            
            if source_idx < len(nodes) and target_idx < len(nodes):
                edges.append(GraphEdge(
                    source=nodes[source_idx].id,
                    target=nodes[target_idx].id,
                    weight=edge_data["weight"],
                    label=edge_data.get("label")
                ))
        
        # Compute cluster statistics
        cluster_stats = {}
        for cluster_id in set(cluster_labels):
            cluster_nodes = [i for i, c in enumerate(cluster_labels) if c == cluster_id]
            cluster_stats[str(cluster_id)] = {
                "size": len(cluster_nodes),
                "color": CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)],
                "nodes": cluster_nodes
            }
        
        return KnowledgeGraphResponse(
            nodes=nodes,
            edges=edges,
            clusters=cluster_stats,
            metadata={
                "total_points": len(points),
                "total_edges": len(edges),
                "total_clusters": len(cluster_stats),
                "collection_info": collection_info.dict(),
                "vector_size": collection_info.config.params.vectors.size if hasattr(collection_info.config.params, 'vectors') else "unknown"
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching knowledge graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching knowledge graph: {str(e)}")

@router.get("/stats")
async def get_graph_stats():
    """Get basic statistics about the knowledge graph"""
    try:
        client = get_qdrant_client()
        
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if "Opal_db_1000" not in collection_names:
            return {
                "collection_exists": False,
                "available_collections": collection_names
            }
        
        # Get collection info
        collection_info = client.get_collection("Opal_db_1000")
        
        # Get a sample of points to analyze
        sample_points = client.scroll(
            collection_name="Opal_db_1000",
            limit=10,
            with_payload=True
        )[0]
        
        # Analyze payload structure
        payload_keys = set()
        for point in sample_points:
            if point.payload:
                payload_keys.update(point.payload.keys())
        
        return {
            "collection_exists": True,
            "total_points": collection_info.points_count,
            "vector_size": collection_info.config.params.vectors.size if hasattr(collection_info.config.params, 'vectors') else "unknown",
            "payload_keys": list(payload_keys),
            "collection_status": collection_info.status,
            "optimizer_status": collection_info.optimizer_status
        }
        
    except Exception as e:
        logger.error(f"Error fetching graph stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching graph stats: {str(e)}")

@router.post("/search", response_model=KnowledgeGraphResponse)
async def search_knowledge_graph(filter_request: GraphFilterRequest):
    """
    Search and filter the knowledge graph
    """
    try:
        return await get_knowledge_graph(
            limit=filter_request.limit,
            min_similarity=filter_request.min_similarity,
            search_query=filter_request.search_query
        )
        
    except Exception as e:
        logger.error(f"Error searching knowledge graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching knowledge graph: {str(e)}")
