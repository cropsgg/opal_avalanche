from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.monitoring import get_health_status, get_metrics, get_error_summary
from app.core.security import current_user

router = APIRouter()


class HealthStatus(BaseModel):
    overall_status: str
    components: Dict[str, Any]
    timestamp: float


class SystemMetrics(BaseModel):
    active_connections: int
    request_rate: float
    error_rate: float
    average_response_time: float


@router.get("/")
async def basic_health():
    """Basic health check endpoint"""
    return {"status": "ok", "service": "opal-backend"}


@router.get("/detailed", response_model=HealthStatus)
async def detailed_health():
    """Detailed health check for all components"""
    try:
        health_data = await get_health_status()
        return HealthStatus(**health_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/database")
async def database_health():
    """Database-specific health check"""
    from app.core.monitoring import health_checker
    
    try:
        db_health = await health_checker.check_database_health()
        
        if db_health["status"] == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is unhealthy"
            )
        
        return db_health
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database health check failed: {str(e)}"
        )


@router.get("/qdrant")
async def qdrant_health():
    """Qdrant vector database health check"""
    from app.core.monitoring import health_checker
    
    try:
        qdrant_health = await health_checker.check_qdrant_health()
        
        if qdrant_health["status"] == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Qdrant is unhealthy"
            )
        
        return qdrant_health
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Qdrant health check failed: {str(e)}"
        )


@router.get("/external-services")
async def external_services_health():
    """Check health of external services"""
    from app.core.monitoring import health_checker
    
    try:
        openai_health = await health_checker.check_openai_health()
        supabase_health = await health_checker.check_supabase_health()
        redis_health = await health_checker.check_redis_health()
        
        services = {
            "openai": openai_health,
            "supabase": supabase_health,
            "redis": redis_health
        }
        
        # Determine overall status
        statuses = [service["status"] for service in services.values()]
        
        if any(status == "unhealthy" for status in statuses):
            overall_status = "degraded"
        elif all(status == "healthy" for status in statuses):
            overall_status = "healthy"
        else:
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "services": services
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"External services health check failed: {str(e)}"
        )


@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    try:
        metrics_data = get_metrics()
        return Response(content=metrics_data, media_type="text/plain")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate metrics: {str(e)}"
        )


@router.get("/errors")
async def error_summary(
    hours: int = 24,
    user=Depends(current_user)  # Require authentication for error logs
):
    """Get error summary (authenticated endpoint)"""
    
    if hours < 1 or hours > 168:  # Max 1 week
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hours must be between 1 and 168"
        )
    
    try:
        error_data = await get_error_summary(hours)
        return error_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get error summary: {str(e)}"
        )


@router.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe"""
    from app.core.monitoring import health_checker
    
    try:
        # Check critical components only
        db_health = await health_checker.check_database_health()
        
        if db_health["status"] == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready - database unhealthy"
            )
        
        return {
            "status": "ready",
            "timestamp": db_health["timestamp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Readiness check failed: {str(e)}"
        )


@router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe"""
    
    try:
        # Simple liveness check - just verify the app is responding
        import time
        
        return {
            "status": "alive",
            "timestamp": time.time(),
            "uptime": "unknown"  # Would need startup time tracking
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Liveness check failed: {str(e)}"
        )


@router.get("/dependencies")
async def dependency_status():
    """Check status of all external dependencies"""
    from app.core.monitoring import health_checker
    
    try:
        dependencies = {
            "database": await health_checker.check_database_health(),
            "qdrant": await health_checker.check_qdrant_health(),
            "redis": await health_checker.check_redis_health(),
            "openai": await health_checker.check_openai_health(),
            "supabase": await health_checker.check_supabase_health()
        }
        
        # Count healthy/unhealthy dependencies
        healthy_count = sum(1 for dep in dependencies.values() if dep["status"] == "healthy")
        unhealthy_count = sum(1 for dep in dependencies.values() if dep["status"] == "unhealthy")
        degraded_count = sum(1 for dep in dependencies.values() if dep["status"] == "degraded")
        
        return {
            "dependencies": dependencies,
            "summary": {
                "total": len(dependencies),
                "healthy": healthy_count,
                "degraded": degraded_count,
                "unhealthy": unhealthy_count
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dependency status check failed: {str(e)}"
        )


# Import Response for metrics endpoint
from fastapi import Response
