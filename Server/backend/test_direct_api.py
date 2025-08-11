#!/usr/bin/env python3
"""
Direct test of knowledge graph functionality
"""

import sys
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

try:
    from qdrant_client import QdrantClient
    
    # Connect directly to Qdrant
    client = QdrantClient(url="http://localhost:6333")
    print("✅ Connected to Qdrant")
    
    # Check collections
    collections = client.get_collections()
    print(f"✅ Collections: {[c.name for c in collections.collections]}")
    
    # Get collection info
    collection_info = client.get_collection("Opal_db_1000")
    print(f"✅ Collection points: {collection_info.points_count}")
    
    # Get first few points to test
    points = client.scroll(
        collection_name="Opal_db_1000",
        limit=3,
        with_payload=True,
        with_vectors=False
    )[0]
    
    print(f"✅ Retrieved {len(points)} points")
    
    # Display sample data
    for i, point in enumerate(points):
        payload = point.payload
        print(f"\n📄 Case {i+1}:")
        print(f"   Title: {payload.get('title', 'Unknown')[:80]}...")
        print(f"   Court: {payload.get('court', 'Unknown')}")
        print(f"   Date: {payload.get('date', 'Unknown')}")
        print(f"   3D Position: ({payload.get('position_x', 0):.1f}, {payload.get('position_y', 0):.1f}, {payload.get('position_z', 0):.1f})")
        print(f"   Blockchain Hash: {payload.get('blockchain_hash', 'Unknown')[:20]}...")
        print(f"   Cluster: {payload.get('cluster', 'Unknown')}")
    
    print("\n🎉 Knowledge Graph data is ready!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
