"""
Merkle tree implementation for legal content integrity verification
Used for notarization of research evidence and audit data
"""
from __future__ import annotations

import re
from typing import List
from eth_utils import keccak


def para_hash(text: str) -> bytes:
    """
    Generate deterministic hash for a paragraph of legal text
    
    Normalizes text to ensure consistent hashing regardless of:
    - Leading/trailing whitespace
    - Multiple consecutive spaces
    - Case differences (optional)
    
    Args:
        text: Input text paragraph
        
    Returns:
        32-byte Keccak-256 hash
    """
    if not text:
        # Empty or None text gets a special empty hash
        return keccak(b"")
    
    # Normalize text
    normalized = text.strip()
    
    # Replace multiple whitespace with single space
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # If still empty after normalization, use empty hash
    if not normalized:
        return keccak(b"")
    
    # Hash the normalized text
    return keccak(normalized.encode('utf-8'))


def merkle_root(hashes: List[bytes]) -> bytes:
    """
    Compute Merkle root from a list of leaf hashes
    
    Implementation:
    - Empty list returns zero hash
    - Single hash returns that hash
    - Pairs hashes and recursively hashes upward
    - Odd numbers duplicate the last hash
    
    Args:
        hashes: List of 32-byte hash values
        
    Returns:
        32-byte Merkle root hash
    """
    if not hashes:
        return b'\x00' * 32
    
    if len(hashes) == 1:
        return hashes[0]
    
    # Work on a copy to avoid modifying input
    current_level = hashes[:]
    
    while len(current_level) > 1:
        next_level = []
        
        # Process pairs
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            
            if i + 1 < len(current_level):
                # We have a pair
                right = current_level[i + 1]
            else:
                # Odd number - duplicate the last hash
                right = left
            
            # Hash the concatenation
            combined_hash = keccak(left + right)
            next_level.append(combined_hash)
        
        current_level = next_level
    
    return current_level[0]


def compute_evidence_merkle_root(retrieval_set: List[dict]) -> str:
    """
    Compute Merkle root from OPAL retrieval evidence
    
    Args:
        retrieval_set: List of evidence items with 'text' field
        
    Returns:
        Hex-encoded Merkle root (0x-prefixed)
    """
    if not retrieval_set:
        return "0x" + "00" * 32
    
    # Extract text and hash each piece of evidence
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


def verify_merkle_proof(leaf_hash: bytes, proof: List[bytes], root: bytes) -> bool:
    """
    Verify a Merkle proof
    
    Args:
        leaf_hash: Hash of the leaf being proven
        proof: List of sibling hashes from leaf to root
        root: Expected Merkle root
        
    Returns:
        True if proof is valid
    """
    current_hash = leaf_hash
    
    for sibling_hash in proof:
        # Determine order (smaller hash goes first for consistency)
        if current_hash <= sibling_hash:
            current_hash = keccak(current_hash + sibling_hash)
        else:
            current_hash = keccak(sibling_hash + current_hash)
    
    return current_hash == root


def generate_merkle_proof(hashes: List[bytes], leaf_index: int) -> List[bytes]:
    """
    Generate Merkle proof for a specific leaf
    
    Args:
        hashes: All leaf hashes in the tree
        leaf_index: Index of the leaf to prove
        
    Returns:
        List of sibling hashes needed for proof
    """
    if not hashes or leaf_index >= len(hashes):
        return []
    
    proof = []
    current_level = hashes[:]
    current_index = leaf_index
    
    while len(current_level) > 1:
        # Find sibling index
        if current_index % 2 == 0:
            # Left child, sibling is right
            sibling_index = current_index + 1
        else:
            # Right child, sibling is left
            sibling_index = current_index - 1
        
        # Add sibling to proof if it exists
        if sibling_index < len(current_level):
            proof.append(current_level[sibling_index])
        else:
            # Odd number case - sibling is the same as current
            proof.append(current_level[current_index])
        
        # Build next level
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            next_level.append(keccak(left + right))
        
        current_level = next_level
        current_index = current_index // 2
    
    return proof
