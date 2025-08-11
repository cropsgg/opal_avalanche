#!/usr/bin/env python3
"""
Debug Qdrant connection for knowledge graph
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

try:
    from app.storage.qdrant_client import get_qdrant
    print("✅ Successfully imported storage client")
    
    client = get_qdrant()
    print("✅ Storage client connected")
    
    collections = client.get_collections()
    print(f"✅ Collections: {[c.name for c in collections.collections]}")
    
    # Test the knowledge graph client
    from app.api.knowledge_graph import get_qdrant_client
    print("✅ Successfully imported knowledge graph client")
    
    kg_client = get_qdrant_client()
    print("✅ Knowledge graph client connected")
    
    kg_collections = kg_client.get_collections()
    print(f"✅ KG Collections: {[c.name for c in kg_collections.collections]}")
    
    # Test collection access
    collection_info = kg_client.get_collection("Opal_db_1000")
    print(f"✅ Collection info: {collection_info.points_count} points")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
