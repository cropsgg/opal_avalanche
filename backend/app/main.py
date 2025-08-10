from __future__ import annotations

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import init_observability
from app.core.security import current_user, extract_bearer, verify_jwt

from app.api.v1 import analytics as analytics_router
from app.api.v1 import chat as chat_router
from app.api.v1 import documents as documents_router
from app.api.v1 import exports as exports_router
from app.api.v1 import health as health_router
from app.api.v1 import matters as matters_router
from app.api.v1 import notarization as notarization_router
from app.api.v1 import subnet_notarization as subnet_notarization_router
from app.api.v1 import privacy as privacy_router
from app.api.v1 import runs as runs_router
from app.api.v1 import subscriptions as subscriptions_router
from app.api.v1 import users as users_router


settings = get_settings()
init_observability("opal-backend")

app = FastAPI(title="OPAL Backend", version="0.1")

# Add monitoring middleware
from app.core.monitoring import MetricsMiddleware
app.add_middleware(MetricsMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def clerk_auth(request: Request, call_next):
    # Allow health and metrics without auth
    if request.url.path.startswith(("/health", "/v1/health", "/metrics")):
        return await call_next(request)
    
    # Try to verify token and attach user
    try:
        token = extract_bearer(request)
        claims = verify_jwt(token)
        request.state.user = {"id": claims.get("sub"), "email": claims.get("email")}
    except Exception as e:
        # For development/testing, allow requests without valid tokens to pass through
        # The individual endpoints will handle authentication with current_user dependency
        import structlog
        log = structlog.get_logger()
        log.warning("auth.middleware_bypass", path=request.url.path, error=str(e))
        request.state.user = None
    
    return await call_next(request)


@app.middleware("http")
async def rls_context(request: Request, call_next):
    """Set current user context for Row Level Security"""
    # Skip for health checks and non-authenticated endpoints
    if request.url.path.startswith(("/health", "/v1/health", "/metrics")):
        return await call_next(request)
    
    # Get user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)
    if not user:
        return await call_next(request)
    
    # Set user context for RLS
    from app.db.session import set_current_user
    
    try:
        # Set user context for all database operations in this request
        set_current_user(user["id"])
        
        # Execute request with user context
        response = await call_next(request)
        return response
    except Exception as e:
        # Log error but don't expose internal details
        import structlog
        log = structlog.get_logger()
        log.error("rls_context.error", error=str(e), user_id=user.get("id"))
        raise


@app.get("/health")
async def health():
    return {"ok": True}


app.include_router(health_router.router, prefix="/v1/health", tags=["health"])
app.include_router(users_router.router, prefix="/v1/users", tags=["users"])
app.include_router(matters_router.router, prefix="/v1", tags=["matters"])
app.include_router(documents_router.router, prefix="/v1", tags=["documents"])
app.include_router(chat_router.router, prefix="/v1", tags=["chat"])
app.include_router(runs_router.router, prefix="/v1", tags=["runs"])
app.include_router(notarization_router.router, prefix="/v1", tags=["notarization"])
app.include_router(subnet_notarization_router.router, prefix="/v1", tags=["subnet-notarization"])
app.include_router(exports_router.router, prefix="/v1", tags=["exports"])
app.include_router(privacy_router.router, prefix="/v1/privacy", tags=["privacy"])
app.include_router(subscriptions_router.router, prefix="/v1/subscriptions", tags=["subscriptions"])
app.include_router(analytics_router.router, prefix="/v1/analytics", tags=["analytics"])


from app.retrieval.qdrant_client import ensure_collection  # noqa: E402


# Add global exception handlers
from app.core.error_handling import GlobalExceptionHandler, OpalError

@app.exception_handler(OpalError)
async def opal_exception_handler(request: Request, exc: OpalError):
    return await GlobalExceptionHandler.handle_opal_exception(request, exc)

@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError):
    return await GlobalExceptionHandler.handle_validation_exception(request, exc)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return await GlobalExceptionHandler.handle_generic_exception(request, exc)


@app.on_event("startup")
async def on_startup():
    try:
        ensure_collection()
    except Exception:
        # Avoid startup crash if Qdrant not reachable in dev
        pass

    # Apply rate limiting middleware
    from app.core.rate_limit import rate_limiter  # noqa: WPS433

    app.middleware("http")(rate_limiter(max_per_day=30))

