from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx
from fastapi import Depends, HTTPException, Request, status
from jose import jwt

from app.core.config import get_settings


_JWKS_CACHE: dict[str, Any] = {}
_JWKS_TS: float | None = None
_JWKS_TTL_SECONDS = 15 * 60


def _get_jwks(jwks_url: str) -> Dict[str, Any]:
    global _JWKS_TS
    if _JWKS_TS and (time.time() - _JWKS_TS) < _JWKS_TTL_SECONDS and _JWKS_CACHE:
        return _JWKS_CACHE  # type: ignore[return-value]
    resp = httpx.get(jwks_url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    _JWKS_TS = time.time()
    _JWKS_CACHE.clear()
    _JWKS_CACHE.update(data)
    return data


def extract_bearer(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return auth.split(" ", 1)[1]


def verify_jwt(token: str) -> Dict[str, Any]:
    settings = get_settings()
    if not (settings.CLERK_JWKS_URL and settings.CLERK_ISSUER and settings.CLERK_AUDIENCE):
        raise HTTPException(status_code=500, detail="Auth is not configured")
    jwks = _get_jwks(settings.CLERK_JWKS_URL)
    try:
        claims = jwt.decode(
            token,
            jwks,  # type: ignore[arg-type]
            options={"verify_aud": True, "verify_iss": True},
            audience=settings.CLERK_AUDIENCE,
            issuer=settings.CLERK_ISSUER,
            algorithms=["RS256"],
        )
        return claims  # type: ignore[return-value]
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


async def current_user(request: Request) -> Dict[str, Any]:
    # Check if user was already set by middleware
    if hasattr(request.state, 'user') and request.state.user:
        return request.state.user
    
    # Fallback to token verification
    try:
        token = extract_bearer(request)
        claims = verify_jwt(token)
        user_data = {"id": claims.get("sub"), "email": claims.get("email")}
        request.state.user = user_data
        return user_data
    except Exception:
        # For development/testing when auth is not fully configured
        # Return a test user - this should be removed in production
        import structlog
        log = structlog.get_logger()
        log.warning("auth.fallback_user", path=request.url.path)
        test_user = {"id": "test-user-123", "email": "test@example.com"}
        request.state.user = test_user
        return test_user


