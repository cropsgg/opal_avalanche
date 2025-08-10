from __future__ import annotations

import base64
import hashlib
import os
import secrets
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import structlog

from ..config.settings import get_settings

log = structlog.get_logger()


class SubnetEncryption:
    """
    AES-GCM encryption utilities for secure commits to private subnet
    Implements the encryption scheme described in OPAL Phase 2 spec
    """
    
    def __init__(self):
        self.settings = get_settings()
        self._master_key: bytes | None = None
        self._label_salt: bytes | None = None
    
    def _get_master_key(self) -> bytes:
        """Get or derive master encryption key"""
        if self._master_key is None:
            # Get key from KMS/environment
            key_b64 = getattr(self.settings, 'SUBNET_MASTER_KEY_B64', None)
            if key_b64:
                self._master_key = base64.b64decode(key_b64)
            else:
                # For development, derive from a secret
                app_secret = getattr(self.settings, 'SECRET_KEY', 'dev-secret')
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b'opal-subnet-master-key',
                    iterations=100000,
                )
                self._master_key = kdf.derive(app_secret.encode())
            
            if len(self._master_key) != 32:
                raise ValueError("Master key must be 32 bytes")
            
            log.info("subnet.encryption.key_loaded")
        
        return self._master_key
    
    def _get_label_salt(self) -> bytes:
        """Get salt for label hashing"""
        if self._label_salt is None:
            salt_b64 = getattr(self.settings, 'FHE_SALT_OR_LABEL_SALT_BASE64', None)
            if salt_b64:
                self._label_salt = base64.b64decode(salt_b64)
            else:
                # For development, use a fixed salt derived from master key
                self._label_salt = hashlib.sha256(self._get_master_key() + b'label-salt').digest()[:16]
            
            log.info("subnet.encryption.salt_loaded", salt_len=len(self._label_salt))
        
        return self._label_salt
    
    def derive_data_key(self, context: str) -> bytes:
        """Derive a data-specific encryption key from master key and context"""
        master_key = self._get_master_key()
        
        # Use HKDF-like derivation
        info = f"opal-subnet-data-{context}".encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=master_key[:16],  # Use first 16 bytes of master key as salt
            iterations=10000,  # Fewer iterations for derived keys
        )
        
        return kdf.derive(info)
    
    def seal(self, plaintext: bytes, context: str = "default") -> bytes:
        """
        Encrypt data using AES-GCM
        
        Args:
            plaintext: Data to encrypt
            context: Context for key derivation (e.g., "run-audit", "document")
            
        Returns:
            Encrypted data: nonce(12) + ciphertext + tag(16)
        """
        try:
            # Derive key for this context
            key = self.derive_data_key(context)
            
            # Generate random nonce
            nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
            
            # Encrypt
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)  # No additional data
            
            # Return: nonce + ciphertext (which includes auth tag)
            result = nonce + ciphertext
            
            log.debug("subnet.encryption.sealed", 
                     context=context,
                     plaintext_len=len(plaintext),
                     ciphertext_len=len(result))
            
            return result
            
        except Exception as e:
            log.error("subnet.encryption.seal_failed", context=context, error=str(e))
            raise
    
    def unseal(self, ciphertext: bytes, context: str = "default") -> bytes:
        """
        Decrypt data using AES-GCM
        
        Args:
            ciphertext: Encrypted data from seal()
            context: Same context used for encryption
            
        Returns:
            Decrypted plaintext
        """
        try:
            if len(ciphertext) < 28:  # 12 (nonce) + 16 (min tag)
                raise ValueError("Ciphertext too short")
            
            # Derive same key
            key = self.derive_data_key(context)
            
            # Extract nonce and encrypted data
            nonce = ciphertext[:12]
            encrypted_data = ciphertext[12:]
            
            # Decrypt
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, encrypted_data, None)
            
            log.debug("subnet.encryption.unsealed",
                     context=context,
                     ciphertext_len=len(ciphertext),
                     plaintext_len=len(plaintext))
            
            return plaintext
            
        except Exception as e:
            log.error("subnet.encryption.unseal_failed", context=context, error=str(e))
            raise
    
    def label_hash(self, label: str) -> bytes:
        """
        Generate opaque label hash: keccak256(salt || label)
        Outsiders cannot infer the label without knowing the salt
        
        Args:
            label: Semantic label (e.g., "run-audit-v1", "document-content")
            
        Returns:
            32-byte hash that hides the original label
        """
        salt = self._get_label_salt()
        combined = salt + label.encode('utf-8')
        return hashlib.sha3_256(combined).digest()
    
    def data_hash(self, data: bytes) -> bytes:
        """
        Generate integrity hash of plaintext data
        Used for verification without revealing content
        
        Args:
            data: Plaintext data
            
        Returns:
            32-byte SHA3-256 hash
        """
        return hashlib.sha3_256(data).digest()
    
    def seal_json(self, data: dict, context: str = "default") -> Tuple[bytes, bytes, bytes]:
        """
        Convenience method to encrypt JSON data
        
        Args:
            data: Dictionary to encrypt
            context: Encryption context
            
        Returns:
            Tuple of (ciphertext, label_hash, data_hash)
        """
        import json
        
        # Serialize to canonical JSON
        plaintext = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')
        
        # Encrypt
        ciphertext = self.seal(plaintext, context)
        
        # Generate hashes
        label_hash = self.label_hash(context)
        data_hash = self.data_hash(plaintext)
        
        return ciphertext, label_hash, data_hash
    
    def unseal_json(self, ciphertext: bytes, context: str = "default") -> dict:
        """
        Convenience method to decrypt JSON data
        
        Args:
            ciphertext: Encrypted data
            context: Same context used for encryption
            
        Returns:
            Decrypted dictionary
        """
        import json
        
        plaintext = self.unseal(ciphertext, context)
        return json.loads(plaintext.decode('utf-8'))


# Global instance
_subnet_encryption: SubnetEncryption | None = None


def get_subnet_encryption() -> SubnetEncryption:
    """Get global subnet encryption instance"""
    global _subnet_encryption
    if _subnet_encryption is None:
        _subnet_encryption = SubnetEncryption()
    return _subnet_encryption


# Convenience functions
def seal_audit_data(audit_data: dict) -> Tuple[bytes, bytes, bytes]:
    """Encrypt audit data for subnet storage"""
    return get_subnet_encryption().seal_json(audit_data, "run-audit-v1")


def unseal_audit_data(ciphertext: bytes) -> dict:
    """Decrypt audit data from subnet storage"""
    return get_subnet_encryption().unseal_json(ciphertext, "run-audit-v1")


def verify_data_integrity(plaintext: bytes, expected_hash: bytes) -> bool:
    """Verify data integrity using hash"""
    actual_hash = get_subnet_encryption().data_hash(plaintext)
    return actual_hash == expected_hash