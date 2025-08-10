#!/usr/bin/env python3
"""
OPAL Phase 2 Demo Script

Demonstrates the complete private subnet notarization flow:
1. Create a mock research run
2. Compute Merkle root from evidence 
3. Encrypt audit data
4. Publish to Notary contract on private subnet
5. Commit encrypted audit to CommitStore
6. Verify end-to-end integrity

This script shows how OPAL achieves:
- Immutable notarization (Merkle roots on-chain)
- Private audit trails (encrypted commits)  
- Data integrity (hash verification)
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.subnet.client import get_subnet_client
from app.subnet.encryption import get_subnet_encryption, seal_audit_data, unseal_audit_data
from app.notary.merkle import merkle_root, para_hash


def create_mock_run_data() -> dict:
    """Create realistic mock data for a legal research run"""
    
    run_id = str(uuid.uuid4())
    
    return {
        "run_id": run_id,
        "created_at": datetime.utcnow().isoformat(),
        "query": {
            "message": "What are the legal precedents for data privacy violations in India?",
            "mode": "precedent",
            "filters": {"jurisdiction": "india", "year_from": 2018}
        },
        "matter": {
            "title": "TechCorp Data Breach Investigation",
            "language": "en"
        },
        "answer_text": "Based on the analysis of relevant case law, the Supreme Court of India in K.S. Puttaswamy v. Union of India (2017) established privacy as a fundamental right. Subsequent decisions have applied this principle to data protection cases...",
        "confidence": 0.92,
        "retrieval_set": [
            {
                "authority_id": "auth_001",
                "court": "Supreme Court of India",
                "title": "K.S. Puttaswamy v. Union of India",
                "text": "The right to privacy is protected as an intrinsic part of the right to life and personal liberty under Article 21 and as a part of the freedoms guaranteed by Part III of the Constitution.",
                "para_ids": [45, 46],
                "neutral_cite": "(2017) 10 SCC 1",
                "date": "2017-08-24"
            },
            {
                "authority_id": "auth_002", 
                "court": "Delhi High Court",
                "title": "WhatsApp Inc. v. Union of India",
                "text": "Data protection requires both procedural and substantive safeguards to ensure that personal information is not misused or disclosed without consent.",
                "para_ids": [23, 24, 25],
                "neutral_cite": "2019 SCC OnLine Del 7123",
                "date": "2019-04-15"
            },
            {
                "authority_id": "auth_003",
                "court": "Karnataka High Court", 
                "title": "Citizens Forum for Civil Liberties v. State of Karnataka",
                "text": "The collection and processing of personal data must be proportionate to the legitimate purpose and subject to appropriate safeguards.",
                "para_ids": [12, 13],
                "neutral_cite": "2020 SCC OnLine Kar 1456",
                "date": "2020-03-10"
            }
        ],
        "agent_votes": [
            {
                "agent": "precedent",
                "decision": {"recommendation": "strong", "reasoning": "Clear Supreme Court precedent"},
                "confidence": 0.95,
                "aligned": True
            },
            {
                "agent": "statute", 
                "decision": {"recommendation": "moderate", "reasoning": "IT Act 2000 provides framework"},
                "confidence": 0.87,
                "aligned": True
            },
            {
                "agent": "risk",
                "decision": {"recommendation": "high", "reasoning": "Regulatory enforcement increasing"},
                "confidence": 0.91,
                "aligned": True
            }
        ]
    }


def compute_evidence_merkle_root(retrieval_set: list) -> str:
    """Compute Merkle root from evidence text (same as backend logic)"""
    
    if not retrieval_set:
        return "0x" + "00" * 32
    
    hashes = []
    for item in retrieval_set:
        if isinstance(item, dict) and "text" in item:
            text = item["text"]
            if text and text.strip():
                hashes.append(para_hash(text.strip()))
    
    if not hashes:
        return "0x" + "00" * 32
    
    root = merkle_root(hashes)
    return "0x" + root.hex()


async def demo_subnet_flow():
    """Run the complete demo flow"""
    
    print("🚀 OPAL Phase 2 - Private Subnet Demo")
    print("=" * 50)
    
    try:
        # Step 1: Create mock run data
        print("\n📊 Step 1: Creating mock research run...")
        run_data = create_mock_run_data()
        print(f"   Run ID: {run_data['run_id']}")
        print(f"   Query: {run_data['query']['message'][:60]}...")
        print(f"   Evidence items: {len(run_data['retrieval_set'])}")
        print(f"   Agent votes: {len(run_data['agent_votes'])}")
        
        # Step 2: Compute Merkle root
        print("\n🌳 Step 2: Computing Merkle root from evidence...")
        merkle_root_hex = compute_evidence_merkle_root(run_data['retrieval_set'])
        print(f"   Merkle root: {merkle_root_hex}")
        
        # Step 3: Build audit data
        print("\n📋 Step 3: Building audit data...")
        audit_data = {
            "version": "opal-audit-v1",
            "run_id": run_data["run_id"],
            "timestamp": run_data["created_at"],
            "query": run_data["query"],
            "matter": run_data["matter"],
            "answer": {
                "text": run_data["answer_text"],
                "confidence": run_data["confidence"]
            },
            "evidence": {
                "retrieval_set": run_data["retrieval_set"],
                "evidence_count": len(run_data["retrieval_set"])
            },
            "agent_analysis": {
                "votes": run_data["agent_votes"],
                "vote_count": len(run_data["agent_votes"])
            },
            "integrity": {
                "merkle_root": merkle_root_hex,
                "evidence_hash": get_subnet_encryption().data_hash(
                    json.dumps(run_data["retrieval_set"], sort_keys=True).encode()
                ).hex()
            }
        }
        print(f"   Audit data size: {len(json.dumps(audit_data))} bytes")
        
        # Step 4: Encrypt audit data
        print("\n🔒 Step 4: Encrypting audit data...")
        ciphertext, label_hash, data_hash = seal_audit_data(audit_data)
        print(f"   Ciphertext size: {len(ciphertext)} bytes")
        print(f"   Label hash: 0x{label_hash.hex()}")
        print(f"   Data hash: 0x{data_hash.hex()}")
        
        # Step 5: Connect to subnet and publish notary
        print("\n⛓️  Step 5: Publishing to Notary contract...")
        subnet_client = get_subnet_client()
        
        try:
            notary_result = subnet_client.publish_notary(run_data["run_id"], merkle_root_hex)
            print(f"   ✅ Notary published!")
            print(f"   Transaction: {notary_result['transactionHash']}")
            print(f"   Block: {notary_result.get('blockNumber', 'pending')}")
        except Exception as e:
            print(f"   ❌ Notary publish failed: {e}")
            print("   (This is expected if subnet is not running)")
            notary_result = {"transactionHash": "0x" + "ab" * 32, "blockNumber": 12345}
        
        # Step 6: Commit encrypted audit data
        print("\n💾 Step 6: Committing encrypted audit to CommitStore...")
        try:
            commit_result = subnet_client.commit_blob(
                run_data["run_id"], 
                label_hash, 
                ciphertext, 
                data_hash
            )
            print(f"   ✅ Audit committed!")
            print(f"   Transaction: {commit_result['transactionHash']}")
            print(f"   Block: {commit_result.get('blockNumber', 'pending')}")
        except Exception as e:
            print(f"   ❌ Commit failed: {e}")
            print("   (This is expected if subnet is not running)")
            commit_result = {"transactionHash": "0x" + "cd" * 32, "blockNumber": 12346}
        
        # Step 7: Verify data integrity
        print("\n🔍 Step 7: Verifying data integrity...")
        
        # Decrypt and verify
        decrypted_audit = unseal_audit_data(ciphertext)
        
        # Check if decrypted data matches original
        original_json = json.dumps(audit_data, sort_keys=True)
        decrypted_json = json.dumps(decrypted_audit, sort_keys=True)
        integrity_check = (original_json == decrypted_json)
        
        print(f"   Encryption/decryption: {'✅ PASS' if integrity_check else '❌ FAIL'}")
        
        # Verify hashes
        recomputed_merkle = compute_evidence_merkle_root(decrypted_audit["evidence"]["retrieval_set"])
        merkle_check = (recomputed_merkle == merkle_root_hex)
        
        print(f"   Merkle root consistency: {'✅ PASS' if merkle_check else '❌ FAIL'}")
        
        # Step 8: Try to read back from subnet (if available)
        print("\n📖 Step 8: Reading back from subnet...")
        try:
            stored_root = subnet_client.get_notary(run_data["run_id"])
            stored_ciphertext = subnet_client.get_commit(run_data["run_id"])
            
            if stored_root:
                print(f"   ✅ Notary verified: {stored_root}")
                print(f"   Root match: {'✅ PASS' if stored_root.lower() == merkle_root_hex.lower() else '❌ FAIL'}")
            else:
                print("   ⚠️  No notary data found (subnet not accessible)")
            
            if stored_ciphertext:
                print(f"   ✅ Audit data retrieved: {len(stored_ciphertext)} bytes")
                decrypted_stored = unseal_audit_data(stored_ciphertext)
                stored_check = (decrypted_stored == audit_data)
                print(f"   Stored audit match: {'✅ PASS' if stored_check else '❌ FAIL'}")
            else:
                print("   ⚠️  No audit data found (subnet not accessible)")
                
        except Exception as e:
            print(f"   ⚠️  Subnet read failed: {e}")
            print("   (This is expected if subnet is not running)")
        
        # Summary
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("\n📋 Summary:")
        print(f"   Run ID: {run_data['run_id']}")
        print(f"   Merkle Root: {merkle_root_hex}")
        print(f"   Notary TX: {notary_result['transactionHash']}")
        print(f"   Commit TX: {commit_result['transactionHash']}")
        print(f"   Audit Size: {len(ciphertext)} bytes encrypted")
        print(f"   Data Integrity: {'✅ VERIFIED' if integrity_check and merkle_check else '❌ FAILED'}")
        
        print("\n🎯 Key Achievements:")
        print("   • Immutable research evidence (Merkle root on-chain)")
        print("   • Private audit trail (encrypted + opaque labels)")
        print("   • Data integrity guarantees (hash verification)")
        print("   • No public visibility (private subnet)")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def check_environment():
    """Check if required environment variables are set"""
    
    print("🔧 Checking environment...")
    
    required_vars = [
        "SUBNET_RPC",
        "SUBNET_SENDER_PK", 
        "SUBNET_NOTARY_ADDR",
        "SUBNET_COMMIT_ADDR"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"   ⚠️  Missing environment variables: {', '.join(missing)}")
        print("   💡 The demo will run in offline mode (no actual subnet transactions)")
        return False
    else:
        print("   ✅ All environment variables configured")
        return True


if __name__ == "__main__":
    print("Starting OPAL Phase 2 Demo...")
    
    # Check environment
    env_ok = check_environment()
    if not env_ok:
        print("\n📝 To run with actual subnet transactions, set these in your .env:")
        print("   SUBNET_RPC=https://your-private-subnet-rpc")
        print("   SUBNET_SENDER_PK=0x...")
        print("   SUBNET_NOTARY_ADDR=0x...")
        print("   SUBNET_COMMIT_ADDR=0x...")
        print("   SUBNET_REGISTRY_ADDR=0x...")
    
    # Run demo
    success = asyncio.run(demo_subnet_flow())
    
    if success:
        print("\n🎉 Demo completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Demo failed!")
        sys.exit(1)
