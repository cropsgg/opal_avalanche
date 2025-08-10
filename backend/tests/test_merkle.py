"""
Unit tests for Merkle tree computation
Tests deterministic hashing and Merkle root computation
"""

import pytest
from app.notary.merkle import para_hash, merkle_root


class TestParaHash:
    """Test paragraph hashing function"""
    
    def test_para_hash_deterministic(self):
        """Test that para_hash is deterministic"""
        text = "This is a test paragraph with some content."
        
        hash1 = para_hash(text)
        hash2 = para_hash(text)
        
        assert hash1 == hash2
        assert len(hash1) == 32  # keccak256 produces 32 bytes
    
    def test_para_hash_normalization(self):
        """Test that text normalization works correctly"""
        # Different spacing and casing should produce same hash
        text1 = "This  is   a    test."
        text2 = "this is a test."
        text3 = "  THIS   IS   A   TEST.  "
        
        hash1 = para_hash(text1)
        hash2 = para_hash(text2)
        hash3 = para_hash(text3)
        
        assert hash1 == hash2 == hash3
    
    def test_para_hash_empty_string(self):
        """Test para_hash with empty string"""
        hash_result = para_hash("")
        
        assert len(hash_result) == 32
        assert hash_result != b'\x00' * 32  # Should not be all zeros
    
    def test_para_hash_whitespace_only(self):
        """Test para_hash with whitespace only"""
        hash1 = para_hash("   ")
        hash2 = para_hash("\t\n  ")
        hash3 = para_hash("")
        
        # All should normalize to empty string
        assert hash1 == hash2 == hash3
    
    def test_para_hash_different_content(self):
        """Test that different content produces different hashes"""
        text1 = "The Supreme Court held that privacy is a fundamental right."
        text2 = "The High Court held that privacy is a fundamental right."
        
        hash1 = para_hash(text1)
        hash2 = para_hash(text2)
        
        assert hash1 != hash2
    
    def test_para_hash_unicode(self):
        """Test para_hash with Unicode content"""
        unicode_text = "न्यायालय ने निजता को मौलिक अधिकार माना है।"
        
        hash_result = para_hash(unicode_text)
        
        assert len(hash_result) == 32
        
        # Should be deterministic
        assert para_hash(unicode_text) == hash_result


class TestMerkleRoot:
    """Test Merkle root computation"""
    
    def test_merkle_root_empty(self):
        """Test Merkle root with empty input"""
        root = merkle_root([])
        
        assert root == b'\x00' * 32
    
    def test_merkle_root_single_hash(self):
        """Test Merkle root with single hash"""
        single_hash = para_hash("Single item")
        
        root = merkle_root([single_hash])
        
        assert root == single_hash
    
    def test_merkle_root_two_hashes(self):
        """Test Merkle root with two hashes"""
        hash1 = para_hash("First item")
        hash2 = para_hash("Second item")
        
        root = merkle_root([hash1, hash2])
        
        # Should be hash of concatenated hashes
        from eth_utils import keccak
        expected = keccak(hash1 + hash2)
        
        assert root == expected
        assert len(root) == 32
    
    def test_merkle_root_deterministic(self):
        """Test that Merkle root is deterministic"""
        hashes = [
            para_hash("Item 1"),
            para_hash("Item 2"), 
            para_hash("Item 3")
        ]
        
        root1 = merkle_root(hashes)
        root2 = merkle_root(hashes)
        
        assert root1 == root2
    
    def test_merkle_root_order_sensitive(self):
        """Test that Merkle root is sensitive to order"""
        hash1 = para_hash("First")
        hash2 = para_hash("Second")
        
        root1 = merkle_root([hash1, hash2])
        root2 = merkle_root([hash2, hash1])
        
        assert root1 != root2
    
    def test_merkle_root_odd_number(self):
        """Test Merkle root with odd number of hashes"""
        hashes = [
            para_hash("Item 1"),
            para_hash("Item 2"),
            para_hash("Item 3")
        ]
        
        root = merkle_root(hashes)
        
        assert len(root) == 32
        assert root != b'\x00' * 32
        
        # Should be deterministic
        assert merkle_root(hashes) == root
    
    def test_merkle_root_power_of_two(self):
        """Test Merkle root with power of 2 number of hashes"""
        hashes = [
            para_hash(f"Item {i}")
            for i in range(4)  # 2^2 = 4
        ]
        
        root = merkle_root(hashes)
        
        assert len(root) == 32
        assert root != b'\x00' * 32
    
    def test_merkle_root_large_set(self):
        """Test Merkle root with larger set of hashes"""
        hashes = [
            para_hash(f"Evidence item {i}: This is some legal text content.")
            for i in range(17)  # Non-power of 2
        ]
        
        root = merkle_root(hashes)
        
        assert len(root) == 32
        assert root != b'\x00' * 32
        
        # Should be deterministic
        assert merkle_root(hashes) == root
    
    def test_merkle_root_duplicate_handling(self):
        """Test Merkle root with duplicate hashes"""
        hash1 = para_hash("Unique content")
        hash2 = para_hash("Duplicate content")
        
        # Same hash appears twice
        hashes = [hash1, hash2, hash2]
        
        root = merkle_root(hashes)
        
        assert len(root) == 32
        assert root != b'\x00' * 32


class TestIntegration:
    """Test integration between para_hash and merkle_root"""
    
    def test_real_legal_content(self):
        """Test with realistic legal content"""
        legal_texts = [
            "The right to privacy is protected as an intrinsic part of the right to life and personal liberty under Article 21.",
            "Data protection requires both procedural and substantive safeguards to ensure personal information is not misused.",
            "The collection and processing of personal data must be proportionate to the legitimate purpose.",
            "Consent must be free, specific, informed and unambiguous for data processing to be lawful."
        ]
        
        # Hash each paragraph
        hashes = [para_hash(text) for text in legal_texts]
        
        # Compute Merkle root
        root = merkle_root(hashes)
        
        assert len(root) == 32
        assert root != b'\x00' * 32
        
        # Should be deterministic
        hashes2 = [para_hash(text) for text in legal_texts]
        root2 = merkle_root(hashes2)
        assert root == root2
    
    def test_empty_and_whitespace_handling(self):
        """Test handling of empty and whitespace-only content"""
        texts = [
            "Valid content here",
            "",  # Empty
            "   ",  # Whitespace only
            "More valid content",
            "\t\n  ",  # More whitespace
        ]
        
        hashes = [para_hash(text) for text in texts]
        root = merkle_root(hashes)
        
        # Empty and whitespace texts should produce same hash
        assert hashes[1] == hashes[2] == hashes[4]
        
        assert len(root) == 32
    
    def test_case_and_spacing_normalization(self):
        """Test that normalization works in full pipeline"""
        texts1 = [
            "The Supreme Court held...",
            "  THE   SUPREME   COURT   HELD...  ",
            "Different content here"
        ]
        
        texts2 = [
            "the supreme court held...",
            "THE SUPREME COURT HELD...",
            "Different content here"
        ]
        
        root1 = merkle_root([para_hash(text) for text in texts1])
        root2 = merkle_root([para_hash(text) for text in texts2])
        
        assert root1 == root2
    
    def test_incremental_building(self):
        """Test that adding items changes the root predictably"""
        base_texts = ["Item 1", "Item 2"]
        base_root = merkle_root([para_hash(text) for text in base_texts])
        
        extended_texts = ["Item 1", "Item 2", "Item 3"]
        extended_root = merkle_root([para_hash(text) for text in extended_texts])
        
        # Roots should be different
        assert base_root != extended_root
        
        # But both should be valid 32-byte hashes
        assert len(base_root) == 32
        assert len(extended_root) == 32
    
    def test_hex_representation(self):
        """Test hex representation of Merkle root (for API compatibility)"""
        texts = ["Evidence 1", "Evidence 2", "Evidence 3"]
        hashes = [para_hash(text) for text in texts]
        root = merkle_root(hashes)
        
        # Convert to hex as done in the API
        root_hex = "0x" + root.hex()
        
        assert root_hex.startswith("0x")
        assert len(root_hex) == 66  # "0x" + 64 hex chars
        assert all(c in "0123456789abcdef" for c in root_hex[2:].lower())
    
    def test_opal_retrieval_set_format(self):
        """Test with OPAL retrieval set format"""
        retrieval_set = [
            {
                "authority_id": "auth_001",
                "court": "Supreme Court of India",
                "text": "The right to privacy is a fundamental right under the Constitution.",
                "para_ids": [45, 46],
                "neutral_cite": "(2017) 10 SCC 1"
            },
            {
                "authority_id": "auth_002",
                "court": "Delhi High Court", 
                "text": "Data protection requires appropriate safeguards for personal information.",
                "para_ids": [23, 24],
                "neutral_cite": "2019 SCC OnLine Del 7123"
            }
        ]
        
        # Extract text and compute root (as done in the backend)
        hashes = []
        for item in retrieval_set:
            if "text" in item and item["text"].strip():
                hashes.append(para_hash(item["text"].strip()))
        
        root = merkle_root(hashes)
        root_hex = "0x" + root.hex()
        
        assert len(hashes) == 2
        assert len(root) == 32
        assert root_hex.startswith("0x")
        
        # Should be deterministic
        hashes2 = []
        for item in retrieval_set:
            if "text" in item and item["text"].strip():
                hashes2.append(para_hash(item["text"].strip()))
        
        root2 = merkle_root(hashes2)
        assert root == root2
