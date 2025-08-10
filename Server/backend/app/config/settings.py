"""
Server configuration settings
Focused on blockchain and storage operations
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Server configuration settings"""
    
    # Qdrant Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "opal_chunks"
    
    # OpenAI (for embedding generation)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBED_MODEL: str = "text-embedding-3-large"
    
    # Private Avalanche Subnet
    SUBNET_RPC: Optional[str] = None
    SUBNET_CHAIN_ID: int = 43210
    SUBNET_NOTARY_ADDR: Optional[str] = None
    SUBNET_COMMIT_ADDR: Optional[str] = None
    SUBNET_REGISTRY_ADDR: Optional[str] = None
    SUBNET_SENDER_PK: Optional[str] = None
    
    # Subnet Encryption
    SUBNET_MASTER_KEY_B64: Optional[str] = None
    FHE_SALT_OR_LABEL_SALT_BASE64: Optional[str] = None
    SECRET_KEY: str = "dev-secret-key"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
