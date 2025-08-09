from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Postgres / Supabase
    DATABASE_URL: str = Field("sqlite:///test.db", description="SQLAlchemy URL, e.g. postgresql+psycopg://user:pass@host:6543/postgres")
    SUPABASE_URL: str | None = None
    SUPABASE_STORAGE_URL: str | None = None
    SUPABASE_SERVICE_KEY: str | None = None
    SUPABASE_REGION: str | None = None

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "opal_chunks"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # OpenAI
    OPENAI_API_KEY: str | None = None
    OPENAI_EMBED_MODEL: str = "text-embedding-3-large"
    OPENAI_GEN_MODEL: str = "gpt-4o-mini"
    OPENAI_VERIFY_MODEL: str = "gpt-4o"
    
    # Additional Qdrant settings
    COLLECTION_NAME: str = "opal_chunks"
    EMBEDDING_MODEL: str = "all-mpnet-base-v2"
    TOP_K: int = 24
    FINAL_K: int = 12
    BATCH_SIZE: int = 64

    # Clerk
    CLERK_JWKS_URL: str | None = None
    CLERK_ISSUER: str | None = None
    CLERK_AUDIENCE: str | None = None

    # KMS / Encryption
    APP_KMS_KEY_BASE64: str | None = None

    # Avalanche Fuji
    AVALANCHE_RPC: str | None = None
    NOTARY_CONTRACT_ADDRESS: str | None = None
    PUBLISHER_PRIVATE_KEY: str | None = None

    # Exports
    EXPORT_TMP_DIR: str = "/tmp/opal"
    
    # Storage paths
    STORAGE_PATH: str = "./storage"
    RUNS_PATH: str = "./runs"

    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


