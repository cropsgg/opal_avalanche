#!/usr/bin/env python3
"""
OPAL Project Release Registration Script

Registers the current project version, source hash, and artifact hash
in the ProjectRegistry contract on the private subnet.

This provides:
- Immutable record of what code version is running
- Proof that we "frozen-recorded" the project baseline
- Transparency for judges and auditors
"""

import asyncio
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.subnet.client import get_subnet_client


def get_git_commit_hash() -> str:
    """Get current git commit hash as source hash"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback if not in git repo
        print("   ⚠️  Not in git repo, using timestamp-based hash")
        timestamp = datetime.utcnow().isoformat()
        return hashlib.sha256(f"opal-{timestamp}".encode()).hexdigest()


def create_artifact_hash() -> str:
    """Create hash of key project artifacts"""
    
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"
    
    # Files to include in artifact hash
    key_files = [
        "backend/app/main.py",
        "backend/app/core/config.py", 
        "backend/app/subnet/client.py",
        "backend/app/subnet/encryption.py",
        "backend/app/api/v1/subnet_notarization.py",
        "backend/requirements.txt",
        "subnet-contracts/contracts/Notary.sol",
        "subnet-contracts/contracts/CommitStore.sol", 
        "subnet-contracts/contracts/ProjectRegistry.sol"
    ]
    
    hasher = hashlib.sha256()
    
    for file_path in key_files:
        full_path = project_root / file_path
        if full_path.exists():
            with open(full_path, 'rb') as f:
                content = f.read()
                hasher.update(f"{file_path}:".encode())
                hasher.update(content)
                hasher.update(b"\n")
    
    return hasher.hexdigest()


def get_project_version() -> str:
    """Get project version string"""
    
    # Try to get from git tag
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--exact-match"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    
    # Fallback to phase + timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
    return f"phase2-{timestamp}"


async def register_project_release():
    """Register current project state in ProjectRegistry"""
    
    print("📋 OPAL Project Release Registration")
    print("=" * 40)
    
    try:
        # Step 1: Gather project information
        print("\n🔍 Step 1: Gathering project information...")
        
        version = get_project_version()
        source_hash = get_git_commit_hash()
        artifact_hash = create_artifact_hash()
        
        print(f"   Version: {version}")
        print(f"   Source hash: {source_hash[:16]}...")
        print(f"   Artifact hash: {artifact_hash[:16]}...")
        
        # Step 2: Connect to subnet
        print("\n⛓️  Step 2: Connecting to subnet...")
        subnet_client = get_subnet_client()
        
        # Step 3: Register release
        print("\n📝 Step 3: Registering release...")
        
        result = subnet_client.register_release(
            version=version,
            source_hash=source_hash,
            artifact_hash=artifact_hash
        )
        
        print(f"   ✅ Release registered!")
        print(f"   Transaction: {result['transactionHash']}")
        print(f"   Block: {result.get('blockNumber', 'pending')}")
        
        # Step 4: Save local record
        print("\n💾 Step 4: Saving local record...")
        
        release_record = {
            "version": version,
            "source_hash": source_hash,
            "artifact_hash": artifact_hash,
            "registered_at": datetime.utcnow().isoformat(),
            "transaction": {
                "hash": result['transactionHash'],
                "block_number": result.get('blockNumber'),
                "network": "subnet"
            }
        }
        
        records_dir = Path(__file__).parent.parent / "records"
        records_dir.mkdir(exist_ok=True)
        
        record_file = records_dir / f"release_{version.replace('/', '_')}.json"
        with open(record_file, 'w') as f:
            json.dump(release_record, f, indent=2)
        
        print(f"   Record saved: {record_file}")
        
        # Summary
        print("\n" + "=" * 40)
        print("✅ Release registration completed!")
        print("\n📋 Summary:")
        print(f"   Version: {version}")
        print(f"   Source: {source_hash}")
        print(f"   Artifact: {artifact_hash}")
        print(f"   Transaction: {result['transactionHash']}")
        
        print("\n🎯 What this proves:")
        print("   • Immutable record of code version deployed")
        print("   • Source code integrity (git commit hash)")
        print("   • Artifact integrity (key file hashes)")
        print("   • Transparent baseline for judges/auditors")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_environment():
    """Check if required environment variables are set"""
    
    print("🔧 Checking environment...")
    
    required_vars = [
        "SUBNET_RPC",
        "SUBNET_SENDER_PK",
        "SUBNET_REGISTRY_ADDR"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"   ❌ Missing required environment variables:")
        for var in missing:
            print(f"      {var}")
        return False
    else:
        print("   ✅ All required environment variables configured")
        return True


if __name__ == "__main__":
    print("Starting OPAL Release Registration...")
    
    # Check environment
    if not check_environment():
        print("\n📝 Required environment variables:")
        print("   SUBNET_RPC=https://your-private-subnet-rpc")
        print("   SUBNET_SENDER_PK=0x...")
        print("   SUBNET_REGISTRY_ADDR=0x...")
        sys.exit(1)
    
    # Run registration
    success = asyncio.run(register_project_release())
    
    if success:
        print("\n🎉 Release registered successfully!")
        sys.exit(0)
    else:
        print("\n💥 Registration failed!")
        sys.exit(1)
