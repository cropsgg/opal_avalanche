"""
Blockchain API endpoints for Server
Handles subnet notarization, contract interactions, and blockchain operations
"""
from __future__ import annotations

import json
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import structlog

from .auth import get_current_user, UserInfo
from ..blockchain.subnet_client import get_subnet_client
from ..blockchain.encryption import get_subnet_encryption, seal_audit_data
from ..blockchain.merkle import merkle_root, para_hash
from ..storage.qdrant_client import search

log = structlog.get_logger()

router = APIRouter()


class DocumentHashRequest(BaseModel):
    """Request for document hashing"""
    documents: List[Dict[str, Any]]  # List of documents with content and metadata
    
class SubnetNotarizeRequest(BaseModel):
    """Request for subnet notarization"""
    run_id: str
    documents: List[Dict[str, Any]]  # Documents to notarize
    retrieval_set: List[Dict[str, Any]] = []  # Optional evidence
    include_audit_commit: bool = True
    metadata: Dict[str, Any] = {}  # Additional metadata


class DocumentHashResponse(BaseModel):
    """Response from document hashing"""
    documents: List[Dict[str, Any]]  # Documents with computed hashes
    merkle_root: str
    total_documents: int
    gas_estimate: Dict[str, Any]

class SubnetNotarizeResponse(BaseModel):
    """Response from subnet notarization"""
    run_id: str
    merkle_root: str
    notary_tx_hash: str
    notary_block_number: int
    commit_tx_hash: str | None = None
    commit_block_number: int | None = None
    network: str = "subnet"
    gas_used: Dict[str, Any] = {}
    total_cost: str = "0"  # Total gas cost in native currency


class BlockchainStatusResponse(BaseModel):
    """Blockchain network status"""
    network: str
    connected: bool
    chain_id: int | None = None
    latest_block: int | None = None
    contract_addresses: Dict[str, str] = {}


class QdrantSearchRequest(BaseModel):
    """Request for Qdrant vector search"""
    query_text: str
    top_k: int = 10
    filters: Dict[str, Any] = {}


class QdrantSearchResponse(BaseModel):
    """Response from Qdrant search"""
    results: List[Dict[str, Any]]
    total_found: int
    search_time_ms: float


@router.post("/documents/hash", response_model=DocumentHashResponse)
async def hash_documents(req: DocumentHashRequest) -> DocumentHashResponse:
    """
    Hash documents and compute Merkle root without storing on blockchain
    Useful for previewing costs and verifying document integrity
    """
    log.info("documents.hash.start", document_count=len(req.documents))
    
    try:
        # Process each document
        processed_docs = []
        all_hashes = []
        
        for i, doc in enumerate(req.documents):
            content = doc.get("content", "")
            if not content:
                raise HTTPException(
                    status_code=400,
                    detail=f"Document {i} is missing content"
                )
            
            # Compute document hash
            doc_hash = para_hash(content.strip())
            all_hashes.append(doc_hash)
            
            processed_doc = {
                "index": i,
                "title": doc.get("title", f"Document {i+1}"),
                "content_preview": content[:100] + "..." if len(content) > 100 else content,
                "content_length": len(content),
                "hash": "0x" + doc_hash.hex(),
                "metadata": doc.get("metadata", {})
            }
            processed_docs.append(processed_doc)
        
        # Compute Merkle root
        merkle_root_hex = "0x" + merkle_root(all_hashes).hex() if all_hashes else "0x" + "00" * 32
        
        # Estimate gas costs
        subnet_client = get_subnet_client()
        gas_estimate = _estimate_gas_costs(len(req.documents), merkle_root_hex)
        
        response = DocumentHashResponse(
            documents=processed_docs,
            merkle_root=merkle_root_hex,
            total_documents=len(req.documents),
            gas_estimate=gas_estimate
        )
        
        log.info("documents.hash.success", 
                document_count=len(req.documents),
                merkle_root=merkle_root_hex)
        
        return response
        
    except Exception as e:
        log.error("documents.hash.failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Document hashing failed: {str(e)}"
        )


@router.post("/subnet/notarize", response_model=SubnetNotarizeResponse)
async def subnet_notarize(
    req: SubnetNotarizeRequest, 
    current_user: UserInfo = Depends(get_current_user)
) -> SubnetNotarizeResponse:
    """
    Notarize documents on the private Avalanche subnet
    Server pays all gas fees
    
    1. Computes Merkle root from documents and evidence
    2. Publishes root to Notary contract on subnet
    3. Optionally encrypts and commits full audit data
    """
    log.info("subnet.notarize.start", 
             run_id=req.run_id,
             document_count=len(req.documents),
             include_audit=req.include_audit_commit,
             user_id=current_user.user_id)
    
    try:
        # Step 1: Process documents and compute Merkle root
        all_content = []
        
        # Add documents
        for doc in req.documents:
            content = doc.get("content", "")
            if content and content.strip():
                all_content.append({"text": content.strip()})
        
        # Add retrieval evidence
        for item in req.retrieval_set:
            if isinstance(item, dict) and "text" in item:
                all_content.append(item)
        
        merkle_root_hex = _compute_evidence_merkle_root(all_content)
        
        # Step 2: Publish to Notary contract (server pays gas)
        subnet_client = get_subnet_client()
        notary_result = subnet_client.publish_notary(req.run_id, merkle_root_hex)
        
        gas_used = {"notary": notary_result.get("gasUsed", 0)}
        total_cost_wei = 0
        
        # Step 3: Optionally commit encrypted audit data
        commit_result = None
        if req.include_audit_commit:
            audit_data = _build_comprehensive_audit_data(
                req.run_id, 
                req.documents, 
                req.retrieval_set, 
                req.metadata
            )
            commit_result = await _commit_audit_data(req.run_id, audit_data)
            gas_used["commit"] = commit_result.get("gasUsed", 0)
        
        # Calculate total cost
        total_gas = sum(gas_used.values())
        # Estimate cost based on gas used (approximate)
        estimated_cost_wei = total_gas * 25_000_000  # 25 gwei per gas
        total_cost = f"{estimated_cost_wei / 1e18:.8f} AVAX"
        
        response = SubnetNotarizeResponse(
            run_id=req.run_id,
            merkle_root=merkle_root_hex,
            notary_tx_hash=notary_result["transactionHash"],
            notary_block_number=notary_result.get("blockNumber", 0),
            commit_tx_hash=commit_result["transactionHash"] if commit_result else None,
            commit_block_number=commit_result.get("blockNumber") if commit_result else None,
            gas_used=gas_used,
            total_cost=total_cost
        )
        
        log.info("subnet.notarize.success",
                run_id=req.run_id,
                merkle_root=merkle_root_hex,
                notary_tx=notary_result["transactionHash"],
                commit_tx=commit_result["transactionHash"] if commit_result else None,
                total_gas=total_gas,
                cost=total_cost)
        
        return response
        
    except Exception as e:
        log.error("subnet.notarize.failed", 
                 run_id=req.run_id, 
                 error=str(e), 
                 error_type=type(e).__name__)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Notarization failed: {str(e)}"
        )


@router.get("/subnet/notary/{run_id}")
async def get_notarization(run_id: str) -> Dict[str, Any]:
    """Get notarization proof from subnet"""
    
    try:
        subnet_client = get_subnet_client()
        subnet_root = subnet_client.get_notary(run_id)
        
        return {
            "run_id": run_id,
            "merkle_root": subnet_root,
            "verified": subnet_root is not None,
            "network": "subnet"
        }
        
    except Exception as e:
        log.warning("subnet.verify.failed", run_id=run_id, error=str(e))
        return {
            "run_id": run_id,
            "merkle_root": None,
            "verified": False,
            "network": "subnet",
            "error": str(e)
        }


@router.get("/subnet/audit/{run_id}")
async def get_audit_data(run_id: str) -> Dict[str, Any]:
    """Retrieve and decrypt audit data from subnet CommitStore"""
    
    try:
        subnet_client = get_subnet_client()
        ciphertext = subnet_client.get_commit(run_id)
        
        if not ciphertext:
            return {
                "run_id": run_id,
                "audit_data": None,
                "encrypted": True,
                "available": False
            }
        
        # Decrypt audit data
        encryption = get_subnet_encryption()
        audit_data = encryption.unseal_json(ciphertext, "run-audit-v1")
        
        return {
            "run_id": run_id,
            "audit_data": audit_data,
            "encrypted": True,
            "available": True,
            "ciphertext_size": len(ciphertext)
        }
        
    except Exception as e:
        log.error("subnet.audit.decrypt_failed", run_id=run_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit data"
        )


@router.get("/status", response_model=BlockchainStatusResponse)
async def get_blockchain_status() -> BlockchainStatusResponse:
    """Get blockchain network status and connectivity"""
    
    try:
        subnet_client = get_subnet_client()
        
        # Test connection
        web3 = subnet_client._get_web3()
        connected = web3.is_connected()
        chain_id = web3.eth.chain_id if connected else None
        latest_block = web3.eth.block_number if connected else None
        
        # Get contract addresses from deployment
        contract_addresses = {}
        try:
            import json
            from pathlib import Path
            deployment_file = Path(__file__).parent.parent / "blockchain" / "deployment.json"
            if deployment_file.exists():
                with open(deployment_file) as f:
                    deployment = json.load(f)
                    contract_addresses = deployment.get("contracts", {})
        except Exception:
            pass
        
        return BlockchainStatusResponse(
            network="subnet",
            connected=connected,
            chain_id=chain_id,
            latest_block=latest_block,
            contract_addresses=contract_addresses
        )
        
    except Exception as e:
        log.error("blockchain.status.failed", error=str(e))
        return BlockchainStatusResponse(
            network="subnet",
            connected=False
        )


@router.post("/search", response_model=QdrantSearchResponse)
async def search_vectors(req: QdrantSearchRequest) -> QdrantSearchResponse:
    """Search Qdrant vector database"""
    
    import time
    start_time = time.time()
    
    try:
        from ..storage.embed import embed_single_query
        
        # Generate query embedding
        query_vector = embed_single_query(req.query_text)
        
        # Search Qdrant
        qdrant_filters = _build_qdrant_filters(req.filters) if req.filters else None
        results = search(query_vector, filters=qdrant_filters, top_k=req.top_k)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            })
        
        search_time_ms = (time.time() - start_time) * 1000
        
        return QdrantSearchResponse(
            results=formatted_results,
            total_found=len(results),
            search_time_ms=search_time_ms
        )
        
    except Exception as e:
        log.error("qdrant.search.failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/register-release")
async def register_project_release(
    version: str,
    source_hash: str,
    artifact_hash: str
) -> Dict[str, Any]:
    """Register a project release on the subnet registry"""
    
    try:
        subnet_client = get_subnet_client()
        result = subnet_client.register_release(version, source_hash, artifact_hash)
        
        return {
            "version": version,
            "source_hash": source_hash,
            "artifact_hash": artifact_hash,
            "tx_hash": result["transactionHash"],
            "block_number": result.get("blockNumber"),
            "registered": True
        }
        
    except Exception as e:
        log.error("subnet.register_release.failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Release registration failed: {str(e)}"
        )


# Helper functions

def _compute_evidence_merkle_root(retrieval_set: List[Dict[str, Any]]) -> str:
    """Compute Merkle root from retrieval evidence"""
    
    if not retrieval_set:
        return "0x" + "00" * 32
    
    # Extract text and hash each paragraph
    hashes = []
    for item in retrieval_set:
        if isinstance(item, dict) and "text" in item:
            text = item["text"]
            if text and text.strip():
                hashes.append(para_hash(text.strip()))
    
    if not hashes:
        return "0x" + "00" * 32
    
    # Compute Merkle root
    root = merkle_root(hashes)
    return "0x" + root.hex()


def _build_audit_data(run_id: str, retrieval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build comprehensive audit data for encryption"""
    
    return {
        "version": "opal-audit-v1",
        "run_id": run_id,
        "timestamp": None,  # Could be added if needed
        "evidence": {
            "retrieval_set": retrieval_set,
            "evidence_count": len(retrieval_set)
        },
        "integrity": {
            "merkle_root": _compute_evidence_merkle_root(retrieval_set),
            "evidence_hash": get_subnet_encryption().data_hash(
                json.dumps(retrieval_set, sort_keys=True).encode()
            ).hex()
        }
    }


def _build_comprehensive_audit_data(
    run_id: str, 
    documents: List[Dict[str, Any]], 
    retrieval_set: List[Dict[str, Any]], 
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Build comprehensive audit data including documents and metadata"""
    
    from datetime import datetime
    
    # Combine all content for integrity check
    all_content = []
    for doc in documents:
        if doc.get("content"):
            all_content.append({"text": doc["content"].strip()})
    all_content.extend(retrieval_set)
    
    return {
        "version": "opal-audit-v2",
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat(),
        "documents": {
            "items": documents,
            "count": len(documents)
        },
        "evidence": {
            "retrieval_set": retrieval_set,
            "evidence_count": len(retrieval_set)
        },
        "metadata": metadata,
        "integrity": {
            "merkle_root": _compute_evidence_merkle_root(all_content),
            "documents_hash": get_subnet_encryption().data_hash(
                json.dumps(documents, sort_keys=True).encode()
            ).hex(),
            "evidence_hash": get_subnet_encryption().data_hash(
                json.dumps(retrieval_set, sort_keys=True).encode()
            ).hex()
        }
    }


def _estimate_gas_costs(num_documents: int, merkle_root: str) -> Dict[str, Any]:
    """Estimate gas costs for notarization operations"""
    
    # Base gas costs (estimated)
    notary_base_gas = 50000  # Base cost for notary publish
    commit_base_gas = 100000  # Base cost for commit
    commit_per_kb_gas = 20000  # Additional cost per KB of data
    
    # Estimate data size for commit (rough estimate)
    estimated_audit_size_kb = max(1, num_documents * 2)  # 2KB per document estimate
    commit_gas = commit_base_gas + (estimated_audit_size_kb * commit_per_kb_gas)
    
    # Gas price (25 gwei)
    gas_price_wei = 25_000_000_000
    
    notary_cost_wei = notary_base_gas * gas_price_wei
    commit_cost_wei = commit_gas * gas_price_wei
    total_cost_wei = notary_cost_wei + commit_cost_wei
    
    return {
        "notary": {
            "gas_limit": notary_base_gas,
            "gas_price_gwei": 25,
            "cost_wei": notary_cost_wei,
            "cost_avax": f"{notary_cost_wei / 1e18:.8f}"
        },
        "commit": {
            "gas_limit": commit_gas,
            "gas_price_gwei": 25,
            "cost_wei": commit_cost_wei,
            "cost_avax": f"{commit_cost_wei / 1e18:.8f}",
            "estimated_data_size_kb": estimated_audit_size_kb
        },
        "total": {
            "gas_limit": notary_base_gas + commit_gas,
            "cost_wei": total_cost_wei,
            "cost_avax": f"{total_cost_wei / 1e18:.8f}"
        },
        "note": "Server pays all gas fees. Estimates may vary based on actual transaction complexity."
    }


async def _commit_audit_data(commit_id: str, audit_data: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypt and commit audit data to subnet"""
    
    # Encrypt audit data
    ciphertext, label_hash, data_hash = seal_audit_data(audit_data)
    
    # Commit to subnet
    subnet_client = get_subnet_client()
    return subnet_client.commit_blob(commit_id, label_hash, ciphertext, data_hash)


def _build_qdrant_filters(filters: Dict[str, Any]) -> Dict[str, Any] | None:
    """Build Qdrant filters from request filters"""
    
    qdrant_filters = {"must": []}
    
    if "court" in filters and filters["court"]:
        qdrant_filters["must"].append({
            "key": "court",
            "match": {"value": filters["court"]}
        })
    
    if "date_from" in filters or "date_to" in filters:
        date_filter = {"key": "date", "range": {}}
        if "date_from" in filters:
            date_filter["range"]["gte"] = filters["date_from"]
        if "date_to" in filters:
            date_filter["range"]["lte"] = filters["date_to"]
        qdrant_filters["must"].append(date_filter)
    
    if "statute_tags" in filters and filters["statute_tags"]:
        for tag in filters["statute_tags"]:
            qdrant_filters["must"].append({
                "key": "statute_tags",
                "match": {"value": tag}
            })
    
    return qdrant_filters if qdrant_filters["must"] else None
