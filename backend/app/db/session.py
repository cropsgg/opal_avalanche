from __future__ import annotations

from typing import AsyncGenerator, Optional
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from app.core.config import get_settings

# Context variable to store current user ID for RLS
current_user_id: ContextVar[Optional[str]] = ContextVar('current_user_id', default=None)


def _normalize_url(url: str) -> str:
    # Expect psycopg3 driver; do not convert to asyncpg to avoid extra dependency
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


_settings = get_settings()
ASYNC_DATABASE_URL = _normalize_url(_settings.DATABASE_URL)
engine = create_async_engine(ASYNC_DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        # Set user context for RLS if available
        user_id = current_user_id.get()
        if user_id:
            try:
                await session.execute(text("SELECT set_config('app.current_user_id', :user_id, true)"), 
                                    {"user_id": user_id})
            except Exception:
                # If setting fails, continue without RLS context
                # This allows the app to work even if RLS is not fully configured
                pass
        
        yield session


def set_current_user(user_id: str) -> None:
    """Set current user ID for RLS context"""
    current_user_id.set(user_id)


def get_current_user() -> Optional[str]:
    """Get current user ID from context"""
    return current_user_id.get()


async def get_db_with_user(user_id: str) -> AsyncGenerator[AsyncSession, None]:
    """Get database session with specific user context for RLS"""
    async with SessionLocal() as session:
        try:
            await session.execute(text("SELECT set_config('app.current_user_id', :user_id, true)"), 
                                {"user_id": user_id})
        except Exception:
            # If setting fails, continue without RLS context
            pass
        
        yield session


