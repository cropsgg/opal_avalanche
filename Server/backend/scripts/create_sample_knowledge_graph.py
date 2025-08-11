#!/usr/bin/env python3
"""
Create sample knowledge graph data for OPAL Server demo
Populates Qdrant with legal document vectors for visualization
"""

import asyncio
import os
import sys
import json
from pathlib import Path
import numpy as np
from typing import List, Dict, Any

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    print("✅ Qdrant client imported successfully")
except ImportError as e:
    print(f"❌ Failed to import qdrant_client: {e}")
    sys.exit(1)

def generate_mock_embedding(text: str, dim: int = 384) -> List[float]:
    """Generate a mock embedding vector based on text content"""
    # Simple hash-based embedding for demo purposes
    # In production, this would use OpenAI API or similar
    hash_val = hash(text)
    np.random.seed(abs(hash_val) % (2**32))
    
    # Generate random vector and normalize
    vector = np.random.normal(0, 1, dim)
    vector = vector / np.linalg.norm(vector)
    
    return vector.tolist()

def create_sample_legal_documents() -> List[Dict[str, Any]]:
    """Create sample legal documents for the knowledge graph"""
    
    documents = [
        {
            "id": "doc_001",
            "text": "The Supreme Court of India in K.S. Puttaswamy v. Union of India (2017) established privacy as a fundamental right under Article 21 of the Constitution. This landmark judgment recognized that privacy is intrinsic to life and liberty.",
            "court": "Supreme Court of India",
            "title": "K.S. Puttaswamy v. Union of India - Privacy Rights",
            "date": "2017-08-24",
            "authority_id": "SC_2017_10_1",
            "statute_tags": ["Article 21", "Privacy Law", "Fundamental Rights"],
            "category": "constitutional_law"
        },
        {
            "id": "doc_002", 
            "text": "In Shreya Singhal v. Union of India (2015), the Supreme Court struck down Section 66A of the IT Act 2000, holding that it violated freedom of speech and expression. The Court emphasized that restrictions on speech must be narrowly tailored.",
            "court": "Supreme Court of India",
            "title": "Shreya Singhal v. Union of India - Freedom of Speech",
            "date": "2015-03-24",
            "authority_id": "SC_2015_5_1",
            "statute_tags": ["Article 19", "IT Act", "Freedom of Speech"],
            "category": "constitutional_law"
        },
        {
            "id": "doc_003",
            "text": "The Delhi High Court in WhatsApp Inc. v. Union of India (2019) addressed data localization requirements and cross-border data transfers. The court emphasized the need for adequate safeguards when transferring personal data.",
            "court": "Delhi High Court", 
            "title": "WhatsApp Inc. v. Union of India - Data Localization",
            "date": "2019-04-15",
            "authority_id": "DHC_2019_123",
            "statute_tags": ["Data Protection", "Cross-border Transfer", "IT Act"],
            "category": "data_protection"
        },
        {
            "id": "doc_004",
            "text": "Section 43A of the Information Technology Act, 2000 imposes liability on body corporates for negligent handling of sensitive personal data. Compensation must be paid for wrongful loss or wrongful gain due to data breaches.",
            "court": "Statutory Provision",
            "title": "IT Act Section 43A - Data Protection Liability", 
            "date": "2008-10-27",
            "authority_id": "IT_ACT_43A",
            "statute_tags": ["Section 43A", "Data Breach", "Compensation"],
            "category": "cyber_law"
        },
        {
            "id": "doc_005",
            "text": "The Bombay High Court in Karmanya Singh Sareen v. Union of India (2020) dealt with issues of surveillance and privacy in the context of Aadhaar linkage. The court balanced security concerns with privacy rights.",
            "court": "Bombay High Court",
            "title": "Karmanya Singh Sareen v. Union of India - Aadhaar Privacy",
            "date": "2020-01-15", 
            "authority_id": "BHC_2020_45",
            "statute_tags": ["Aadhaar", "Surveillance", "Privacy"],
            "category": "privacy_law"
        },
        {
            "id": "doc_006",
            "text": "In Bharti Airtel Ltd. v. TRAI (2019), the Delhi High Court examined telecom regulations and consumer protection. The judgment addressed issues of service quality and customer grievance redressal mechanisms.",
            "court": "Delhi High Court",
            "title": "Bharti Airtel Ltd. v. TRAI - Telecom Regulation",
            "date": "2019-07-10",
            "authority_id": "DHC_2019_78",
            "statute_tags": ["TRAI", "Telecom Law", "Consumer Protection"],
            "category": "telecom_law"
        },
        {
            "id": "doc_007",
            "text": "The Karnataka High Court in Citizens Forum for Civil Liberties v. State of Karnataka (2020) addressed issues of mass surveillance and proportionality. The court emphasized that surveillance measures must be proportionate to legitimate aims.",
            "court": "Karnataka High Court",
            "title": "Citizens Forum v. State of Karnataka - Surveillance", 
            "date": "2020-03-10",
            "authority_id": "KHC_2020_67",
            "statute_tags": ["Surveillance", "Proportionality", "Civil Liberties"],
            "category": "privacy_law"
        },
        {
            "id": "doc_008",
            "text": "Section 69 of the Information Technology Act, 2000 provides the framework for lawful interception and monitoring of computer resources. The provision requires adherence to procedural safeguards and judicial oversight.",
            "court": "Statutory Provision",
            "title": "IT Act Section 69 - Lawful Interception",
            "date": "2008-10-27", 
            "authority_id": "IT_ACT_69",
            "statute_tags": ["Section 69", "Interception", "Judicial Oversight"],
            "category": "cyber_law"
        },
        {
            "id": "doc_009",
            "text": "The Madras High Court in Tamil Nadu Technology Services v. State of Tamil Nadu (2021) dealt with government technology procurement and data security requirements. The court stressed the importance of robust security standards.",
            "court": "Madras High Court",
            "title": "Tamil Nadu Technology Services - Data Security",
            "date": "2021-02-28",
            "authority_id": "MHC_2021_34",
            "statute_tags": ["Government Procurement", "Data Security", "Technology"],
            "category": "government_law"
        },
        {
            "id": "doc_010",
            "text": "In Facebook Inc. v. Union of India (2020), the Delhi High Court examined social media intermediary liability and content moderation obligations. The judgment clarified the scope of safe harbor provisions under IT Act.",
            "court": "Delhi High Court", 
            "title": "Facebook Inc. v. Union of India - Intermediary Liability",
            "date": "2020-09-15",
            "authority_id": "DHC_2020_156",
            "statute_tags": ["Intermediary Liability", "Content Moderation", "Safe Harbor"],
            "category": "cyber_law"
        },
        {
            "id": "doc_011",
            "text": "The concept of digital rights as fundamental rights was explored in Anuradha Bhasin v. Union of India (2020) where the Supreme Court recognized that internet access facilitates exercise of fundamental rights including freedom of speech.",
            "court": "Supreme Court of India",
            "title": "Anuradha Bhasin v. Union of India - Digital Rights",
            "date": "2020-01-10",
            "authority_id": "SC_2020_3_1", 
            "statute_tags": ["Digital Rights", "Internet Access", "Article 19"],
            "category": "constitutional_law"
        },
        {
            "id": "doc_012",
            "text": "The Personal Data Protection Bill 2019 proposed comprehensive data protection framework including data localization, consent mechanisms, and rights of data principals. The bill aimed to regulate processing of personal data.",
            "court": "Legislative Proposal",
            "title": "Personal Data Protection Bill 2019 - Overview", 
            "date": "2019-12-11",
            "authority_id": "PDP_BILL_2019",
            "statute_tags": ["Data Protection", "Consent", "Data Localization"],
            "category": "data_protection"
        },
        {
            "id": "doc_013",
            "text": "The Gujarat High Court in Cyber Crime Investigation Cell v. Accused (2021) dealt with digital evidence preservation and chain of custody in cybercrime cases. The court established protocols for handling electronic evidence.",
            "court": "Gujarat High Court",
            "title": "Cyber Crime Investigation - Digital Evidence",
            "date": "2021-05-20",
            "authority_id": "GHC_2021_89",
            "statute_tags": ["Digital Evidence", "Chain of Custody", "Cybercrime"],
            "category": "criminal_law"
        },
        {
            "id": "doc_014",
            "text": "In Microsoft Corporation v. Taxation Officer (2018), the Delhi High Court addressed issues of cloud computing taxation and permanent establishment. The judgment clarified tax implications of cloud services.",
            "court": "Delhi High Court",
            "title": "Microsoft Corporation - Cloud Computing Taxation",
            "date": "2018-11-25",
            "authority_id": "DHC_2018_234",
            "statute_tags": ["Cloud Computing", "Taxation", "Permanent Establishment"],
            "category": "tax_law"
        },
        {
            "id": "doc_015",
            "text": "The Calcutta High Court in Online Gaming Association v. State of West Bengal (2021) examined the legality of online gaming and gambling. The court distinguished between games of skill and games of chance.",
            "court": "Calcutta High Court",
            "title": "Online Gaming Association - Gaming Legality",
            "date": "2021-08-12", 
            "authority_id": "CHC_2021_156",
            "statute_tags": ["Online Gaming", "Gambling", "Games of Skill"],
            "category": "gaming_law"
        }
    ]
    
    return documents

async def create_qdrant_collection():
    """Create and populate Qdrant collection with sample data"""
    
    print("🔧 Creating Qdrant collection...")
    
    try:
        # Connect to Qdrant
        client = QdrantClient(url="http://localhost:6333")
        
        # Check connection
        collections = client.get_collections()
        print(f"   ✅ Connected to Qdrant. Existing collections: {len(collections.collections)}")
        
        collection_name = "Opal_db_1000"
        vector_size = 384  # Standard embedding dimension
        
        # Delete collection if it exists
        try:
            client.delete_collection(collection_name)
            print(f"   🗑️  Deleted existing collection: {collection_name}")
        except Exception:
            pass  # Collection doesn't exist
        
        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )
        print(f"   ✅ Created collection: {collection_name}")
        
        # Get sample documents
        documents = create_sample_legal_documents()
        print(f"   📄 Prepared {len(documents)} sample documents")
        
        # Create points for Qdrant
        points = []
        for i, doc in enumerate(documents):
            # Generate embedding
            embedding = generate_mock_embedding(doc["text"], vector_size)
            
            # Create point
            point = models.PointStruct(
                id=i + 1,  # Qdrant point ID
                vector=embedding,
                payload={
                    "doc_id": doc["id"],
                    "text": doc["text"],
                    "court": doc["court"],
                    "title": doc["title"],
                    "date": doc["date"],
                    "authority_id": doc["authority_id"],
                    "statute_tags": doc["statute_tags"],
                    "category": doc["category"]
                }
            )
            points.append(point)
        
        # Upload points to Qdrant
        operation_result = client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        print(f"   ✅ Uploaded {len(points)} points to collection")
        print(f"   🎯 Operation status: {operation_result.status}")
        
        # Verify collection
        collection_info = client.get_collection(collection_name)
        print(f"   📊 Collection info:")
        print(f"      - Points count: {collection_info.points_count}")
        print(f"      - Vector size: {collection_info.config.params.vectors.size}")
        print(f"      - Distance metric: {collection_info.config.params.vectors.distance}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to create collection: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_knowledge_graph_api():
    """Test the knowledge graph API endpoints"""
    
    print("\n🧪 Testing Knowledge Graph API...")
    
    try:
        import requests
        
        base_url = "http://localhost:8001"
        
        # Test stats endpoint
        print("   📊 Testing /api/v1/knowledge-graph/stats...")
        stats_response = requests.get(f"{base_url}/api/v1/knowledge-graph/stats")
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"      ✅ Stats API working")
            print(f"      - Collection exists: {stats.get('collection_exists')}")
            print(f"      - Total points: {stats.get('total_points')}")
            print(f"      - Vector size: {stats.get('vector_size')}")
        else:
            print(f"      ❌ Stats API failed: {stats_response.status_code}")
        
        # Test main endpoint
        print("   🕸️  Testing /api/v1/knowledge-graph/...")
        graph_response = requests.get(f"{base_url}/api/v1/knowledge-graph/?limit=10")
        
        if graph_response.status_code == 200:
            graph_data = graph_response.json()
            print(f"      ✅ Graph API working")
            print(f"      - Nodes: {len(graph_data.get('nodes', []))}")
            print(f"      - Edges: {len(graph_data.get('edges', []))}")
            print(f"      - Clusters: {len(graph_data.get('clusters', {}))}")
        else:
            print(f"      ❌ Graph API failed: {graph_response.status_code}")
            print(f"      Response: {graph_response.text}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False

async def main():
    """Main execution function"""
    
    print("🚀 OPAL Knowledge Graph Setup")
    print("=" * 50)
    
    # Step 1: Create collection and data
    print("\n📊 Step 1: Setting up Qdrant collection...")
    success = await create_qdrant_collection()
    
    if not success:
        print("❌ Failed to create Qdrant collection")
        return False
    
    # Step 2: Test API
    print("\n🧪 Step 2: Testing Knowledge Graph API...")
    api_success = await test_knowledge_graph_api()
    
    if not api_success:
        print("⚠️  API tests failed, but collection was created")
    
    # Step 3: Summary
    print("\n" + "=" * 50)
    print("✅ Knowledge Graph setup completed!")
    print("\n🎯 What was created:")
    print("   • Qdrant collection: 'Opal_db_1000'")
    print("   • Sample legal documents: 15 cases")
    print("   • Mock embeddings: 384-dimensional vectors")
    print("   • Rich metadata: court, date, statute tags")
    
    print("\n🌐 Access the Knowledge Graph:")
    print("   • Frontend: http://localhost:3001/knowledge-graph")
    print("   • API: http://localhost:8001/api/v1/knowledge-graph/")
    print("   • Stats: http://localhost:8001/api/v1/knowledge-graph/stats")
    
    print("\n💡 Next steps:")
    print("   • Refresh the frontend to see the visualization")
    print("   • Try filtering by different parameters")
    print("   • Explore node connections and clusters")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Setup failed!")
        sys.exit(1)
