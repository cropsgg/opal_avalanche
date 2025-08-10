"""
Unit tests for subnet encryption utilities
Tests AES-GCM encryption, label hashing, and data integrity
"""

import json
import os
import pytest
from unittest.mock import patch

from app.subnet.encryption import (
    SubnetEncryption,
    get_subnet_encryption,
    seal_audit_data,
    unseal_audit_data,
    verify_data_integrity
)


class TestSubnetEncryption:
    """Test encryption functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Use test keys for predictable results
        self.test_master_key = b'a' * 32  # 32 bytes
        self.test_salt = b'b' * 16        # 16 bytes
        
        with patch.dict(os.environ, {
            'SUBNET_MASTER_KEY_B64': 'YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWE=',  # base64(b'a'*32)
            'FHE_SALT_OR_LABEL_SALT_BASE64': 'YmJiYmJiYmJiYmJiYmJiYg=='  # base64(b'b'*16)
        }):
            self.encryption = SubnetEncryption()
    
    def test_seal_and_unseal_basic(self):
        """Test basic encryption and decryption"""
        plaintext = b"Hello, private subnet!"
        context = "test"
        
        # Encrypt
        ciphertext = self.encryption.seal(plaintext, context)
        
        # Should be longer than plaintext (nonce + ciphertext + tag)
        assert len(ciphertext) > len(plaintext)
        assert len(ciphertext) >= 28  # 12 (nonce) + 16 (min tag) + data
        
        # Decrypt
        decrypted = self.encryption.unseal(ciphertext, context)
        
        assert decrypted == plaintext
    
    def test_seal_empty_data(self):
        """Test encryption of empty data"""
        plaintext = b""
        context = "empty"
        
        ciphertext = self.encryption.seal(plaintext, context)
        decrypted = self.encryption.unseal(ciphertext, context)
        
        assert decrypted == plaintext
    
    def test_different_contexts_different_keys(self):
        """Test that different contexts produce different encryptions"""
        plaintext = b"Same data, different contexts"
        
        ciphertext1 = self.encryption.seal(plaintext, "context1")
        ciphertext2 = self.encryption.seal(plaintext, "context2")
        
        # Should be different due to different derived keys
        assert ciphertext1 != ciphertext2
        
        # But both should decrypt correctly
        assert self.encryption.unseal(ciphertext1, "context1") == plaintext
        assert self.encryption.unseal(ciphertext2, "context2") == plaintext
    
    def test_wrong_context_fails(self):
        """Test that wrong context fails to decrypt"""
        plaintext = b"Secret data"
        
        ciphertext = self.encryption.seal(plaintext, "correct")
        
        # Wrong context should fail
        with pytest.raises(Exception):  # Cryptography will raise an exception
            self.encryption.unseal(ciphertext, "wrong")
    
    def test_label_hash_deterministic(self):
        """Test that label hashing is deterministic"""
        label = "run-audit-v1"
        
        hash1 = self.encryption.label_hash(label)
        hash2 = self.encryption.label_hash(label)
        
        assert hash1 == hash2
        assert len(hash1) == 32  # SHA3-256
    
    def test_label_hash_different_labels(self):
        """Test that different labels produce different hashes"""
        hash1 = self.encryption.label_hash("label1")
        hash2 = self.encryption.label_hash("label2")
        
        assert hash1 != hash2
        assert len(hash1) == 32
        assert len(hash2) == 32
    
    def test_data_hash_deterministic(self):
        """Test that data hashing is deterministic"""
        data = b"Some data to hash"
        
        hash1 = self.encryption.data_hash(data)
        hash2 = self.encryption.data_hash(data)
        
        assert hash1 == hash2
        assert len(hash1) == 32  # SHA3-256
    
    def test_data_hash_different_data(self):
        """Test that different data produces different hashes"""
        hash1 = self.encryption.data_hash(b"data1")
        hash2 = self.encryption.data_hash(b"data2")
        
        assert hash1 != hash2
    
    def test_seal_json_roundtrip(self):
        """Test JSON encryption and decryption"""
        data = {
            "version": "test-v1",
            "run_id": "test-123",
            "query": {"message": "test query"},
            "nested": {"values": [1, 2, 3]}
        }
        context = "json-test"
        
        ciphertext, label_hash, data_hash = self.encryption.seal_json(data, context)
        
        # Verify return types
        assert isinstance(ciphertext, bytes)
        assert isinstance(label_hash, bytes) 
        assert isinstance(data_hash, bytes)
        assert len(label_hash) == 32
        assert len(data_hash) == 32
        
        # Decrypt and verify
        decrypted = self.encryption.unseal_json(ciphertext, context)
        assert decrypted == data
    
    def test_json_canonical_serialization(self):
        """Test that JSON serialization is canonical (order-independent)"""
        data1 = {"b": 2, "a": 1, "c": 3}
        data2 = {"a": 1, "b": 2, "c": 3}  # Same data, different order
        
        ciphertext1, _, data_hash1 = self.encryption.seal_json(data1, "test")
        ciphertext2, _, data_hash2 = self.encryption.seal_json(data2, "test")
        
        # Data hashes should be the same (canonical JSON)
        assert data_hash1 == data_hash2
        
        # But ciphertext should be different (random nonce)
        assert ciphertext1 != ciphertext2
        
        # Both should decrypt to the same logical data
        decrypted1 = self.encryption.unseal_json(ciphertext1, "test")
        decrypted2 = self.encryption.unseal_json(ciphertext2, "test")
        assert decrypted1 == decrypted2


class TestGlobalFunctions:
    """Test global convenience functions"""
    
    def test_seal_unseal_audit_data(self):
        """Test audit data specific functions"""
        audit_data = {
            "version": "opal-audit-v1",
            "run_id": "test-run-123",
            "evidence": {"items": ["item1", "item2"]},
            "integrity": {"hash": "abc123"}
        }
        
        ciphertext, label_hash, data_hash = seal_audit_data(audit_data)
        
        # Verify structure
        assert isinstance(ciphertext, bytes)
        assert len(label_hash) == 32
        assert len(data_hash) == 32
        
        # Decrypt
        decrypted = unseal_audit_data(ciphertext)
        assert decrypted == audit_data
    
    def test_verify_data_integrity(self):
        """Test data integrity verification"""
        original_data = b"Important data to verify"
        
        # Get correct hash
        encryption = get_subnet_encryption()
        correct_hash = encryption.data_hash(original_data)
        
        # Verify with correct hash
        assert verify_data_integrity(original_data, correct_hash) is True
        
        # Verify with wrong hash
        wrong_hash = b"0" * 32
        assert verify_data_integrity(original_data, wrong_hash) is False
    
    def test_get_subnet_encryption_singleton(self):
        """Test that get_subnet_encryption returns same instance"""
        instance1 = get_subnet_encryption()
        instance2 = get_subnet_encryption()
        
        assert instance1 is instance2


class TestErrorHandling:
    """Test error handling in encryption"""
    
    def test_invalid_ciphertext_too_short(self):
        """Test handling of invalid ciphertext"""
        encryption = SubnetEncryption()
        
        with pytest.raises(ValueError, match="Ciphertext too short"):
            encryption.unseal(b"short", "test")
    
    def test_corrupted_ciphertext(self):
        """Test handling of corrupted ciphertext"""
        encryption = SubnetEncryption()
        
        # Create valid ciphertext then corrupt it
        plaintext = b"Valid data"
        ciphertext = encryption.seal(plaintext, "test")
        
        # Corrupt the ciphertext
        corrupted = bytearray(ciphertext)
        corrupted[15] ^= 0xFF  # Flip bits in the middle
        
        with pytest.raises(Exception):  # Should raise cryptographic exception
            encryption.unseal(bytes(corrupted), "test")


class TestConfigurationHandling:
    """Test configuration and key handling"""
    
    def test_missing_master_key_fallback(self):
        """Test fallback when master key is not configured"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('app.core.config.get_settings') as mock_settings:
                mock_settings.return_value.SECRET_KEY = "test-secret"
                
                encryption = SubnetEncryption()
                # Should not raise an error, should derive from SECRET_KEY
                key = encryption._get_master_key()
                assert len(key) == 32
    
    def test_missing_salt_fallback(self):
        """Test fallback when salt is not configured"""
        with patch.dict(os.environ, {
            'SUBNET_MASTER_KEY_B64': 'YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWE='
        }):
            encryption = SubnetEncryption()
            # Should derive salt from master key
            salt = encryption._get_label_salt()
            assert len(salt) == 16
    
    def test_invalid_master_key_length(self):
        """Test error on invalid master key length"""
        with patch.dict(os.environ, {
            'SUBNET_MASTER_KEY_B64': 'c2hvcnQ='  # base64("short") - too short
        }):
            encryption = SubnetEncryption()
            with pytest.raises(ValueError, match="Master key must be 32 bytes"):
                encryption._get_master_key()


class TestRealWorldScenarios:
    """Test realistic usage scenarios"""
    
    def test_large_audit_data(self):
        """Test encryption of large audit data"""
        # Create large audit data (similar to real OPAL run)
        large_audit = {
            "version": "opal-audit-v1",
            "run_id": "large-test-run",
            "evidence": {
                "retrieval_set": [
                    {
                        "authority_id": f"auth_{i}",
                        "text": "A" * 1000,  # 1KB of text per item
                        "metadata": {"para_ids": list(range(10))}
                    }
                    for i in range(50)  # 50 items = ~50KB total
                ]
            },
            "agent_votes": [
                {"agent": f"agent_{i}", "decision": {"score": 0.9}, "confidence": 0.85}
                for i in range(10)
            ]
        }
        
        # Should handle large data without issues
        ciphertext, label_hash, data_hash = seal_audit_data(large_audit)
        
        assert len(ciphertext) > 50000  # Should be large
        assert len(label_hash) == 32
        assert len(data_hash) == 32
        
        # Should decrypt correctly
        decrypted = unseal_audit_data(ciphertext)
        assert decrypted == large_audit
    
    def test_unicode_handling(self):
        """Test handling of Unicode data"""
        unicode_data = {
            "message": "Legal analysis with émojis 🏛️ and हिंदी text",
            "court": "न्यायालय",
            "symbols": "§ © ® ™ € £ ¥"
        }
        
        ciphertext, _, _ = seal_audit_data(unicode_data)
        decrypted = unseal_audit_data(ciphertext)
        
        assert decrypted == unicode_data
    
    def test_multiple_contexts_isolation(self):
        """Test that different contexts are properly isolated"""
        sensitive_data = {"secret": "very important"}
        
        # Encrypt with different contexts
        contexts = ["run-audit-v1", "document-content", "user-data"]
        ciphertexts = {}
        
        for context in contexts:
            ct, lh, dh = get_subnet_encryption().seal_json(sensitive_data, context)
            ciphertexts[context] = (ct, lh, dh)
        
        # All should be different
        assert len(set(ct for ct, _, _ in ciphertexts.values())) == len(contexts)
        assert len(set(lh for _, lh, _ in ciphertexts.values())) == len(contexts)
        
        # But all should decrypt correctly with their own context
        for context, (ct, _, _) in ciphertexts.items():
            decrypted = get_subnet_encryption().unseal_json(ct, context)
            assert decrypted == sensitive_data
