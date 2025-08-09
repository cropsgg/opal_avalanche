from __future__ import annotations

import base64
import os
from typing import Dict, Optional, Any
import structlog
import json

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings

log = structlog.get_logger()


class EnvelopeEncryption:
    """
    Application-level envelope encryption for user inputs using AES-GCM
    Implements KMS-style envelope encryption with random data keys
    """
    
    def __init__(self, master_key_b64: Optional[str] = None):
        """Initialize with base64-encoded master key"""
        settings = get_settings()
        if master_key_b64:
            self.master_key = base64.b64decode(master_key_b64)
        elif settings.APP_KMS_KEY_BASE64:
            self.master_key = base64.b64decode(settings.APP_KMS_KEY_BASE64)
        else:
            # Generate a new master key for development (NOT for production)
            log.warning("encryption.no_master_key", msg="Generating new master key - NOT for production use")
            self.master_key = AESGCM.generate_key(bit_length=256)
            log.info("encryption.master_key_generated", 
                    key_b64=base64.b64encode(self.master_key).decode()[:16] + "...")
    
    def encrypt_data(self, plaintext: str, additional_data: Optional[str] = None) -> Dict[str, str]:
        """
        Encrypt data using envelope encryption
        Returns dict with encrypted data and metadata
        """
        try:
            # Generate random 256-bit data key
            data_key = AESGCM.generate_key(bit_length=256)
            
            # Create AEAD cipher with data key
            aesgcm_data = AESGCM(data_key)
            
            # Generate random nonce for data encryption
            nonce = os.urandom(12)  # 96 bits for AES-GCM
            
            # Prepare additional authenticated data
            aad = additional_data.encode() if additional_data else b""
            
            # Encrypt plaintext with data key
            ciphertext = aesgcm_data.encrypt(nonce, plaintext.encode(), aad)
            
            # Encrypt data key with master key (envelope encryption)
            aesgcm_master = AESGCM(self.master_key)
            key_nonce = os.urandom(12)
            encrypted_data_key = aesgcm_master.encrypt(key_nonce, data_key, None)
            
            # Return encrypted package
            result = {
                "ciphertext": base64.b64encode(ciphertext).decode(),
                "nonce": base64.b64encode(nonce).decode(),
                "encrypted_key": base64.b64encode(encrypted_data_key).decode(),
                "key_nonce": base64.b64encode(key_nonce).decode(),
                "algorithm": "AES-GCM",
                "version": "1.0"
            }
            
            if additional_data:
                result["aad"] = additional_data
            
            log.debug("encryption.encrypt_success", 
                     plaintext_length=len(plaintext),
                     ciphertext_length=len(ciphertext))
            
            return result
            
        except Exception as e:
            log.error("encryption.encrypt_error", error=str(e))
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_package: Dict[str, str]) -> str:
        """
        Decrypt data using envelope encryption
        Takes encrypted package and returns plaintext
        """
        try:
            # Extract components
            ciphertext = base64.b64decode(encrypted_package["ciphertext"])
            nonce = base64.b64decode(encrypted_package["nonce"])
            encrypted_data_key = base64.b64decode(encrypted_package["encrypted_key"])
            key_nonce = base64.b64decode(encrypted_package["key_nonce"])
            
            # Get additional authenticated data if present
            aad = encrypted_package.get("aad", "").encode() if encrypted_package.get("aad") else b""
            
            # Decrypt data key with master key
            aesgcm_master = AESGCM(self.master_key)
            data_key = aesgcm_master.decrypt(key_nonce, encrypted_data_key, None)
            
            # Decrypt ciphertext with data key
            aesgcm_data = AESGCM(data_key)
            plaintext_bytes = aesgcm_data.decrypt(nonce, ciphertext, aad)
            
            plaintext = plaintext_bytes.decode()
            
            log.debug("encryption.decrypt_success", 
                     ciphertext_length=len(ciphertext),
                     plaintext_length=len(plaintext))
            
            return plaintext
            
        except Exception as e:
            log.error("encryption.decrypt_error", error=str(e))
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_json(self, data: Dict[str, Any], additional_data: Optional[str] = None) -> Dict[str, str]:
        """Encrypt JSON-serializable data"""
        json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        return self.encrypt_data(json_str, additional_data)
    
    def decrypt_json(self, encrypted_package: Dict[str, str]) -> Dict[str, Any]:
        """Decrypt and parse JSON data"""
        json_str = self.decrypt_data(encrypted_package)
        return json.loads(json_str)
    
    def crypto_shred(self, encrypted_package: Dict[str, str]) -> bool:
        """
        Crypto-shred by making the data unrecoverable
        In practice, this involves securely deleting the encrypted data key
        """
        try:
            # Overwrite sensitive fields with random data
            if "encrypted_key" in encrypted_package:
                # Overwrite the encrypted key to make data unrecoverable
                random_key = base64.b64encode(os.urandom(32)).decode()
                encrypted_package["encrypted_key"] = random_key
                encrypted_package["shredded"] = True
                encrypted_package["shredded_at"] = str(int(os.time.time()))
                
                log.info("encryption.crypto_shred_success")
                return True
            
            return False
            
        except Exception as e:
            log.error("encryption.crypto_shred_error", error=str(e))
            return False


# Global encryption instance
_encryption_instance: Optional[EnvelopeEncryption] = None


def get_encryption() -> EnvelopeEncryption:
    """Get global encryption instance (singleton)"""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = EnvelopeEncryption()
    return _encryption_instance


def encrypt_user_input(plaintext: str, user_id: Optional[str] = None) -> Dict[str, str]:
    """
    Encrypt user input with optional user context as additional authenticated data
    """
    additional_data = f"user:{user_id}" if user_id else None
    return get_encryption().encrypt_data(plaintext, additional_data)


def decrypt_user_input(encrypted_package: Dict[str, str]) -> str:
    """
    Decrypt user input
    """
    return get_encryption().decrypt_data(encrypted_package)


def encrypt_pii_data(data: Dict[str, Any], user_id: str) -> Dict[str, str]:
    """
    Encrypt PII data with user context
    """
    additional_data = f"pii:user:{user_id}"
    return get_encryption().encrypt_json(data, additional_data)


def decrypt_pii_data(encrypted_package: Dict[str, str]) -> Dict[str, Any]:
    """
    Decrypt PII data
    """
    return get_encryption().decrypt_json(encrypted_package)


# Utility functions for database column encryption
class EncryptedField:
    """
    Helper class for encrypting database fields
    Use in SQLAlchemy models for sensitive fields
    """
    
    def __init__(self, value: Optional[str] = None, encrypted_package: Optional[Dict[str, str]] = None):
        self._encrypted_package = encrypted_package
        self._plaintext = value
        self._is_encrypted = encrypted_package is not None
    
    @property
    def encrypted_package(self) -> Optional[Dict[str, str]]:
        """Get encrypted package for database storage"""
        if not self._is_encrypted and self._plaintext:
            self._encrypted_package = encrypt_user_input(self._plaintext)
            self._is_encrypted = True
        return self._encrypted_package
    
    @property
    def plaintext(self) -> Optional[str]:
        """Get decrypted plaintext"""
        if self._is_encrypted and self._encrypted_package:
            if not self._plaintext:
                self._plaintext = decrypt_user_input(self._encrypted_package)
        return self._plaintext
    
    def __str__(self) -> str:
        return self.plaintext or ""
    
    def __repr__(self) -> str:
        return f"EncryptedField(encrypted={self._is_encrypted})"


def generate_master_key() -> str:
    """
    Generate a new master key for encryption
    This should be done once and stored securely in environment
    """
    key = AESGCM.generate_key(bit_length=256)
    key_b64 = base64.b64encode(key).decode()
    
    log.info("encryption.master_key_generated", 
            key_preview=key_b64[:16] + "...",
            length=len(key_b64))
    
    return key_b64


if __name__ == "__main__":
    # Test the encryption system
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "generate-key":
        print("Generated master key:")
        print(generate_master_key())
        print("\nAdd this to your .env file as:")
        print("APP_KMS_KEY_BASE64=<generated_key>")
    else:
        # Test encryption/decryption
        enc = EnvelopeEncryption()
        
        test_data = "This is sensitive user input that needs encryption"
        print(f"Original: {test_data}")
        
        encrypted = enc.encrypt_data(test_data, "user:test123")
        print(f"Encrypted package: {encrypted}")
        
        decrypted = enc.decrypt_data(encrypted)
        print(f"Decrypted: {decrypted}")
        
        assert test_data == decrypted, "Encryption/decryption failed"
        print("✅ Encryption test passed")
