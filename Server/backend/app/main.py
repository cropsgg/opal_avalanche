"""
OPAL Server - Blockchain and Vector Database Operations
Handles subnet notarization, contract interactions, and Qdrant search
"""
from __future__ import annotations

import structlog
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.blockchain import router as blockchain_router
from .api.knowledge_graph import router as knowledge_graph_router
from .api.auth import router as auth_router, cleanup_expired_sessions
from .config.settings import get_settings
from .storage.qdrant_client import ensure_collection, health_check as qdrant_health


# Configure structured logging
def setup_logging():
    """Setup structured logging"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    settings = get_settings()
    log = structlog.get_logger()
    
    # Startup
    log.info("server.startup", host=settings.HOST, port=settings.PORT)
    
    # Initialize Qdrant collection
    try:
        ensure_collection()
        log.info("qdrant.collection_ready")
    except Exception as e:
        log.warning("qdrant.collection_init_failed", error=str(e))
    
    # Cleanup expired auth sessions periodically
    cleanup_expired_sessions()
    
    yield
    
    # Shutdown
    log.info("server.shutdown")


# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="OPAL Server",
    description="Blockchain and Vector Database Operations for OPAL",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(blockchain_router, prefix="/api/v1", tags=["blockchain"])
app.include_router(knowledge_graph_router)

# Health check endpoints
@app.get("/health")
async def health():
    """Basic health check"""
    return {"status": "healthy", "service": "opal-server"}


@app.get("/health/detailed")
async def detailed_health():
    """Detailed health check including dependencies"""
    settings = get_settings()
    
    health_status = {
        "service": "opal-server",
        "version": "1.0.0",
        "status": "healthy",
        "components": {}
    }
    
    # Check Qdrant
    qdrant_status = qdrant_health()
    health_status["components"]["qdrant"] = qdrant_status
    
    # Check blockchain connection
    try:
        from .blockchain.subnet_client import get_subnet_client
        subnet_client = get_subnet_client()
        web3 = subnet_client._get_web3()
        health_status["components"]["subnet"] = {
            "status": "healthy" if web3.is_connected() else "unhealthy",
            "connected": web3.is_connected(),
            "chain_id": web3.eth.chain_id if web3.is_connected() else None
        }
    except Exception as e:
        health_status["components"]["subnet"] = {
            "status": "unhealthy",
            "error": str(e),
            "connected": False
        }
    
    # Overall status
    component_statuses = [comp.get("status", "unknown") for comp in health_status["components"].values()]
    if any(status == "unhealthy" for status in component_statuses):
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    from .storage.qdrant_client import get_collection_info
    
    qdrant_info = get_collection_info()
    
    return {
        "qdrant": qdrant_info,
        "timestamp": structlog.processors.TimeStamper().timestamp()
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    log = structlog.get_logger()
    log.error("server.unhandled_exception", 
              path=request.url.path,
              method=request.method,
              error=str(exc),
              error_type=type(exc).__name__)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "OPAL Server",
        "description": "Blockchain and Vector Database Operations",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
