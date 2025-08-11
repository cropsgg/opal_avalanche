#!/usr/bin/env python3
"""
Generate comprehensive Supreme Court demo data for hackathon
Creates 50+ realistic judgments with blockchain hashes and 3D knowledge graph
"""

import asyncio
import json
import hashlib
import uuid
import random
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

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

class SupremeCourtDataGenerator:
    def __init__(self):
        self.judges = [
            "Chief Justice D.Y. Chandrachud", "Justice Sanjay Kishan Kaul", 
            "Justice S. Abdul Nazeer", "Justice B.R. Gavai", "Justice Surya Kant",
            "Justice J.K. Maheshwari", "Justice Hima Kohli", "Justice B.V. Nagarathna",
            "Justice C.T. Ravikumar", "Justice M.M. Sundresh", "Justice Bela M. Trivedi",
            "Justice P.S. Narasimha", "Justice J.B. Pardiwala", "Justice Manoj Misra",
            "Justice S. Ravindra Bhat", "Justice Dipankar Datta", "Justice Rajesh Bindal",
            "Justice Aniruddha Bose", "Justice A.S. Oka", "Justice Vikram Nath"
        ]
        
        self.legal_topics = [
            "Constitutional Law", "Criminal Law", "Civil Rights", "Property Rights",
            "Labor Law", "Environmental Law", "Tax Law", "Corporate Law", 
            "Family Law", "Electoral Law", "Administrative Law", "Banking Law",
            "Intellectual Property", "Privacy Rights", "Digital Rights", "Consumer Protection",
            "Competition Law", "Securities Law", "Arbitration", "Contract Law",
            "Tort Law", "Evidence Law", "Procedure Law", "Fundamental Rights",
            "Directive Principles", "Emergency Powers", "Federal Structure"
        ]
        
        self.legal_articles = [
            "Article 14", "Article 19", "Article 21", "Article 32", "Article 226",
            "Article 136", "Article 141", "Article 142", "Article 368", "Article 370",
            "Section 498A", "Section 377", "Section 124A", "Section 66A", "Section 69A",
            "Right to Information Act", "Consumer Protection Act", "Companies Act",
            "IT Act 2000", "Prevention of Corruption Act", "PMLA", "SARFAESI Act"
        ]

    def generate_case_title(self) -> str:
        """Generate realistic case titles"""
        petitioners = [
            "Union of India", "State of Maharashtra", "State of Delhi", "State of Karnataka",
            "Reserve Bank of India", "Securities and Exchange Board of India", "Central Bureau of Investigation",
            "Enforcement Directorate", "Competition Commission of India", "Telecom Regulatory Authority",
            "National Human Rights Commission", "Central Information Commission", "Election Commission of India",
            "Google LLC", "Facebook Inc.", "Amazon India", "Flipkart Internet", "Paytm Payments",
            "Bharti Airtel Ltd", "Reliance Industries", "Tata Consultancy Services", "Infosys Ltd",
            "Wipro Ltd", "ICICI Bank", "HDFC Bank", "State Bank of India", "Life Insurance Corporation",
            "Indian Railways", "Oil and Natural Gas Corporation", "Coal India Ltd", "Power Grid Corporation",
            "Dr. Prashant Kumar", "Advocate Indira Jaising", "Senior Advocate Kapil Sibal",
            "Citizens Forum for Civil Liberties", "People's Union for Civil Liberties", 
            "Association for Democratic Reforms", "Common Cause", "Centre for Public Interest Litigation",
            "Lawyers Collective", "Human Rights Law Network", "Jan Aushadhi Association",
            "All India Institute of Medical Sciences", "Indian Medical Association", "Bar Council of India",
            "Supreme Court Advocates-on-Record Association", "Delhi High Court Bar Association"
        ]
        
        respondents = [
            "Union of India", "State of Uttar Pradesh", "State of Gujarat", "State of Tamil Nadu",
            "State of West Bengal", "State of Rajasthan", "State of Madhya Pradesh", "State of Bihar",
            "Ministry of Home Affairs", "Ministry of Finance", "Ministry of Electronics and Information Technology",
            "Central Board of Direct Taxes", "Goods and Services Tax Council", "Unique Identification Authority",
            "National Sample Survey Office", "Central Vigilance Commission", "Lokpal", "Central Administrative Tribunal",
            "National Green Tribunal", "National Company Law Tribunal", "Debt Recovery Tribunal",
            "Income Tax Appellate Tribunal", "Central Excise and Service Tax Appellate Tribunal",
            "WhatsApp Inc.", "Twitter Inc.", "YouTube LLC", "Microsoft Corporation", "Apple Inc.",
            "Tesla Motors", "Uber Technologies", "Ola Electric", "Zomato Ltd", "Swiggy Ltd",
            "BigBasket", "Myntra Designs", "Snapdeal Ltd", "MakeMyTrip Ltd", "BookMyShow",
            "BYJU'S", "Unacademy", "Vedantu", "PhonePe", "Razorpay", "Pine Labs"
        ]
        
        petitioner = random.choice(petitioners)
        respondent = random.choice(respondents)
        
        # Ensure petitioner and respondent are different
        while respondent == petitioner:
            respondent = random.choice(respondents)
            
        case_types = ["v.", "vs.", "versus"]
        return f"{petitioner} {random.choice(case_types)} {respondent}"

    def generate_judgment_text(self, case_title: str, topic: str) -> str:
        """Generate realistic judgment text"""
        
        court_openings = [
            "This Court is hearing the present matter under Article 136 of the Constitution of India.",
            "The present Special Leave Petition is filed challenging the impugned judgment and order.",
            "This appeal arises out of the judgment and order passed by the High Court.",
            "The petitioner has approached this Court seeking relief under Article 32 of the Constitution.",
            "This matter has been referred to the Constitutional Bench for authoritative pronouncement.",
            "The present case raises important questions of law having pan-India ramifications.",
            "This Court is seized of the matter involving interpretation of fundamental rights.",
            "The instant petition challenges the constitutional validity of the impugned provisions."
        ]
        
        legal_reasoning = [
            f"Upon careful consideration of the submissions advanced by learned counsel for both parties and perusal of the material on record, this Court finds that the primary issue that arises for determination is the interpretation of {random.choice(self.legal_articles)} and its application to the facts of the present case.",
            
            f"The constitutional principle enshrined in {random.choice(self.legal_articles)} mandates that any restriction on fundamental rights must pass the test of reasonableness and proportionality. The State cannot exercise its power in an arbitrary manner.",
            
            f"This Court has consistently held that the right to {topic.lower()} is an integral part of the fundamental rights guaranteed under Part III of the Constitution. Any legislation that impinges upon this right must be subjected to strict scrutiny.",
            
            f"The doctrine of proportionality requires that the means adopted to achieve a legitimate aim must be proportionate to the end sought to be achieved. The measure adopted by the respondent authorities fails this test.",
            
            f"The Constitution envisages a balance between individual rights and collective good. However, this balance cannot be achieved at the cost of completely extinguishing fundamental rights guaranteed to citizens."
        ]
        
        precedents = [
            "K.S. Puttaswamy v. Union of India (2017) 10 SCC 1",
            "Shreya Singhal v. Union of India (2015) 5 SCC 1", 
            "Anuradha Bhasin v. Union of India (2020) 3 SCC 637",
            "Maneka Gandhi v. Union of India (1978) 1 SCC 248",
            "A.K. Gopalan v. State of Madras AIR 1950 SC 27",
            "Minerva Mills v. Union of India (1980) 3 SCC 625",
            "Kesavananda Bharati v. State of Kerala (1973) 4 SCC 225",
            "S.R. Bommai v. Union of India (1994) 3 SCC 1",
            "I.R. Coelho v. State of Tamil Nadu (2007) 2 SCC 1",
            "Indra Sawhney v. Union of India (1992) Supp (3) SCC 217"
        ]
        
        conclusions = [
            "In view of the above discussion, this Court is of the considered opinion that the impugned action/legislation is constitutionally impermissible and violates the fundamental rights of citizens.",
            
            "Having regard to the principles laid down by this Court in the aforementioned precedents, we find that the respondent authorities have acted beyond their jurisdiction.",
            
            "The constitutional scheme does not permit such arbitrary exercise of power by the State. The rule of law demands adherence to constitutional principles.",
            
            "Democracy and rule of law are basic features of the Constitution which cannot be compromised under any circumstances.",
            
            "This Court must ensure that the delicate balance between individual liberty and State power is maintained in accordance with constitutional principles."
        ]
        
        judgment_text = f"""
{random.choice(court_openings)}

FACTS:
{case_title} involves {topic.lower()} and raises significant constitutional questions regarding the scope and extent of fundamental rights guaranteed under the Constitution of India.

LEGAL ANALYSIS:
{random.choice(legal_reasoning)}

This Court in {random.choice(precedents)} held that fundamental rights are the cornerstone of constitutional democracy. The same principle applies to the facts of the present case.

{random.choice(legal_reasoning)}

PRECEDENTS CONSIDERED:
1. {random.choice(precedents)}
2. {random.choice(precedents)}
3. {random.choice(precedents)}

CONCLUSION:
{random.choice(conclusions)}

OPERATIVE PART:
For the foregoing reasons, this appeal/petition is allowed/dismissed. The impugned judgment and order is set aside/upheld. No order as to costs.

PRONOUNCED ON: {(datetime.now() - timedelta(days=random.randint(1, 1095))).strftime('%B %d, %Y')}
"""
        return judgment_text.strip()

    def generate_blockchain_hash(self, case_data: Dict[str, Any]) -> str:
        """Generate realistic blockchain transaction hash"""
        content = json.dumps(case_data, sort_keys=True).encode()
        hash_obj = hashlib.sha256(content[:1000])  # Simulate blockchain hash
        return "0x" + hash_obj.hexdigest()

    def generate_3d_positions(self, num_points: int, clusters: int = 8) -> List[Tuple[float, float, float]]:
        """Generate 3D positions for knowledge graph visualization"""
        positions = []
        
        # Create cluster centers in 3D space
        cluster_centers = []
        for i in range(clusters):
            angle_xy = (2 * math.pi * i) / clusters
            angle_z = random.uniform(-math.pi/4, math.pi/4)
            
            center_x = 500 * math.cos(angle_xy) * math.cos(angle_z)
            center_y = 500 * math.sin(angle_xy) * math.cos(angle_z) 
            center_z = 300 * math.sin(angle_z)
            
            cluster_centers.append((center_x, center_y, center_z))
        
        # Assign points to clusters and add some randomness
        for i in range(num_points):
            cluster_idx = i % clusters
            center_x, center_y, center_z = cluster_centers[cluster_idx]
            
            # Add gaussian noise around cluster center
            noise_factor = 150
            x = center_x + random.gauss(0, noise_factor)
            y = center_y + random.gauss(0, noise_factor)
            z = center_z + random.gauss(0, noise_factor/2)
            
            positions.append((x, y, z))
        
        return positions

    def generate_mock_embedding(self, text: str, dim: int = 384) -> List[float]:
        """Generate mock embedding vector"""
        hash_val = hash(text)
        np.random.seed(abs(hash_val) % (2**32))
        
        vector = np.random.normal(0, 1, dim)
        vector = vector / np.linalg.norm(vector)
        
        return vector.tolist()

    def generate_supreme_court_cases(self, num_cases: int = 55) -> List[Dict[str, Any]]:
        """Generate comprehensive Supreme Court case data"""
        cases = []
        positions_3d = self.generate_3d_positions(num_cases)
        
        for i in range(num_cases):
            case_title = self.generate_case_title()
            topic = random.choice(self.legal_topics)
            judgment_text = self.generate_judgment_text(case_title, topic)
            
            # Generate realistic case number
            year = random.randint(2020, 2024)
            case_num = random.randint(1, 9999)
            citation = f"({year}) {random.randint(1, 15)} SCC {random.randint(1, 999)}"
            
            # Select random judges (1-5 judge bench)
            bench_size = random.choices([1, 3, 5, 7, 9], weights=[10, 50, 25, 10, 5])[0]
            bench = random.sample(self.judges, min(bench_size, len(self.judges)))
            
            # Generate case data
            case_data = {
                "id": f"sc_{year}_{case_num:04d}",
                "case_title": case_title,
                "citation": citation,
                "court": "Supreme Court of India",
                "bench": bench,
                "date": (datetime.now() - timedelta(days=random.randint(1, 1095))).strftime('%Y-%m-%d'),
                "topic": topic,
                "legal_articles": random.sample(self.legal_articles, random.randint(1, 4)),
                "judgment_text": judgment_text,
                "word_count": len(judgment_text.split()),
                "importance_score": random.uniform(0.6, 1.0),
                "position_3d": {
                    "x": positions_3d[i][0],
                    "y": positions_3d[i][1], 
                    "z": positions_3d[i][2]
                },
                "cluster": i % 8,
                "metadata": {
                    "case_type": random.choice(["Constitutional", "Criminal", "Civil", "Taxation", "Service", "Election"]),
                    "bench_strength": bench_size,
                    "judgment_type": random.choice(["Majority", "Unanimous", "Dissenting"]),
                    "cited_count": random.randint(5, 250),
                    "complexity_score": random.uniform(0.3, 1.0),
                    "legal_domain": topic,
                    "filing_year": year,
                    "disposal_year": year + random.randint(0, 2)
                }
            }
            
            # Generate blockchain hash
            case_data["blockchain_hash"] = self.generate_blockchain_hash(case_data)
            case_data["merkle_root"] = self.generate_blockchain_hash({"merkle_tree": judgment_text})
            
            # Generate mock transaction details
            case_data["blockchain_details"] = {
                "transaction_hash": case_data["blockchain_hash"],
                "block_number": random.randint(18500000, 19000000),
                "gas_used": random.randint(21000, 85000),
                "gas_price_gwei": random.uniform(15.0, 45.0),
                "timestamp": int((datetime.now() - timedelta(days=random.randint(1, 365))).timestamp()),
                "network": "Avalanche C-Chain",
                "chain_id": 43210,
                "contract_address": "0x" + hashlib.sha256(f"notary_{i}".encode()).hexdigest()[:40],
                "cost_avax": f"{random.uniform(0.001, 0.015):.6f}"
            }
            
            cases.append(case_data)
        
        return cases

async def populate_qdrant_with_3d_data(cases: List[Dict[str, Any]]) -> bool:
    """Populate Qdrant with 3D knowledge graph data"""
    try:
        client = QdrantClient(url="http://localhost:6333")
        
        collection_name = "Opal_db_1000"
        vector_size = 384
        
        # Delete and recreate collection for fresh data
        try:
            client.delete_collection(collection_name)
            print(f"   🗑️  Deleted existing collection: {collection_name}")
        except Exception:
            pass
        
        # Create collection with 3D metadata support
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )
        print(f"   ✅ Created collection: {collection_name}")
        
        # Create points with 3D positions
        points = []
        for i, case in enumerate(cases):
            # Generate embedding from judgment text
            embedding = SupremeCourtDataGenerator().generate_mock_embedding(
                case["judgment_text"], vector_size
            )
            
            # Create comprehensive payload with 3D data
            payload = {
                "doc_id": case["id"],
                "text": case["judgment_text"][:2000],  # Truncate for storage
                "title": case["case_title"],
                "citation": case["citation"],
                "court": case["court"],
                "date": case["date"],
                "topic": case["topic"],
                "legal_articles": case["legal_articles"],
                "bench": case["bench"],
                "case_type": case["metadata"]["case_type"],
                "importance_score": case["importance_score"],
                "cited_count": case["metadata"]["cited_count"],
                "complexity_score": case["metadata"]["complexity_score"],
                "word_count": case["word_count"],
                
                # 3D positioning data
                "position_x": case["position_3d"]["x"],
                "position_y": case["position_3d"]["y"], 
                "position_z": case["position_3d"]["z"],
                "cluster": case["cluster"],
                
                # Blockchain data
                "blockchain_hash": case["blockchain_hash"],
                "merkle_root": case["merkle_root"],
                "block_number": case["blockchain_details"]["block_number"],
                "gas_used": case["blockchain_details"]["gas_used"],
                "network": case["blockchain_details"]["network"],
                "contract_address": case["blockchain_details"]["contract_address"],
                
                # Visualization metadata
                "node_size": 20 + (case["importance_score"] * 60),
                "node_color": f"hsl({(case['cluster'] * 45) % 360}, 70%, 60%)",
                "edge_weight": case["metadata"]["complexity_score"]
            }
            
            point = models.PointStruct(
                id=i + 1,
                vector=embedding,
                payload=payload
            )
            points.append(point)
        
        # Upload all points
        operation_result = client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        print(f"   ✅ Uploaded {len(points)} Supreme Court cases")
        print(f"   🎯 Operation status: {operation_result.status}")
        
        # Verify collection
        collection_info = client.get_collection(collection_name)
        print(f"   📊 Collection stats:")
        print(f"      - Points: {collection_info.points_count}")
        print(f"      - Vector dimension: {collection_info.config.params.vectors.size}")
        print(f"      - 3D positions: ✅ Enabled")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to populate Qdrant: {e}")
        import traceback
        traceback.print_exc()
        return False

def save_blockchain_data(cases: List[Dict[str, Any]]) -> bool:
    """Save blockchain data to JSON for frontend display"""
    try:
        blockchain_data = {
            "network": "Avalanche C-Chain Private Subnet",
            "chain_id": 43210,
            "total_cases": len(cases),
            "total_blocks": len(set(case["blockchain_details"]["block_number"] for case in cases)),
            "contracts": {
                "notary": "0xA1B2C3D4E5F6789012345678901234567890ABCD",
                "commit_store": "0x1234567890ABCDEF1234567890ABCDEF12345678",
                "registry": "0xFEDCBA0987654321FEDCBA0987654321FEDCBA09"
            },
            "transactions": []
        }
        
        for case in cases:
            tx_data = {
                "hash": case["blockchain_hash"],
                "case_id": case["id"],
                "case_title": case["case_title"],
                "merkle_root": case["merkle_root"],
                "block_number": case["blockchain_details"]["block_number"],
                "gas_used": case["blockchain_details"]["gas_used"],
                "gas_price_gwei": case["blockchain_details"]["gas_price_gwei"],
                "cost_avax": case["blockchain_details"]["cost_avax"],
                "timestamp": case["blockchain_details"]["timestamp"],
                "contract_address": case["blockchain_details"]["contract_address"],
                "verification_status": "Verified",
                "immutable": True
            }
            blockchain_data["transactions"].append(tx_data)
        
        # Save to file
        output_file = Path(__file__).parent.parent / "data" / "blockchain_demo.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(blockchain_data, f, indent=2)
        
        print(f"   ✅ Saved blockchain data: {output_file}")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to save blockchain data: {e}")
        return False

async def main():
    """Main execution function"""
    print("🚀 Supreme Court Demo Data Generator")
    print("=" * 60)
    
    # Generate case data
    print("\n⚖️  Step 1: Generating Supreme Court cases...")
    generator = SupremeCourtDataGenerator()
    cases = generator.generate_supreme_court_cases(55)
    
    print(f"   ✅ Generated {len(cases)} Supreme Court cases")
    print(f"   📊 Case types: {len(set(case['metadata']['case_type'] for case in cases))} different types")
    print(f"   👨‍⚖️ Judges involved: {len(set(judge for case in cases for judge in case['bench']))} unique judges")
    print(f"   📅 Date range: {min(case['date'] for case in cases)} to {max(case['date'] for case in cases)}")
    
    # Populate Qdrant with 3D data
    print("\n🕸️  Step 2: Creating 3D Knowledge Graph...")
    qdrant_success = await populate_qdrant_with_3d_data(cases)
    
    if not qdrant_success:
        print("❌ Failed to populate knowledge graph")
        return False
    
    # Save blockchain data
    print("\n⛓️  Step 3: Storing blockchain hashes...")
    blockchain_success = save_blockchain_data(cases)
    
    if not blockchain_success:
        print("❌ Failed to save blockchain data")
        return False
    
    # Generate summary statistics
    print("\n📈 Step 4: Generating demo statistics...")
    
    total_words = sum(case["word_count"] for case in cases)
    avg_importance = sum(case["importance_score"] for case in cases) / len(cases)
    total_gas = sum(case["blockchain_details"]["gas_used"] for case in cases)
    total_cost = sum(float(case["blockchain_details"]["cost_avax"]) for case in cases)
    
    print(f"   📄 Total words across all judgments: {total_words:,}")
    print(f"   ⭐ Average importance score: {avg_importance:.3f}")
    print(f"   ⛽ Total gas used: {total_gas:,}")
    print(f"   💰 Total blockchain cost: {total_cost:.6f} AVAX")
    
    # Success summary
    print("\n" + "=" * 60)
    print("✅ Supreme Court Demo Data Generated Successfully!")
    print("\n🎯 What was created:")
    print("   • 55 realistic Supreme Court judgments")
    print("   • Comprehensive blockchain transaction data")
    print("   • 3D-positioned knowledge graph (8 clusters)")
    print("   • Realistic legal citations and precedents")
    print("   • Mock gas fees and transaction hashes")
    print("   • Multi-judge bench compositions")
    
    print("\n🌐 Access the demo:")
    print("   • Knowledge Graph: http://localhost:3001/knowledge-graph")
    print("   • Blockchain: http://localhost:3001/blockchain")
    print("   • API Stats: http://localhost:8001/api/v1/knowledge-graph/stats")
    
    print("\n💡 Demo highlights:")
    print("   • Real Supreme Court judge names")
    print("   • Authentic legal article references")
    print("   • 3D visualization with clusters by legal domain")
    print("   • Blockchain immutability with Avalanche C-Chain")
    print("   • Gas fee transparency and cost tracking")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 Demo data generation completed!")
        print("Your hackathon demo is ready! 🚀")
        sys.exit(0)
    else:
        print("\n💥 Demo generation failed!")
        sys.exit(1)
