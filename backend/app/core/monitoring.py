from __future__ import annotations

import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
import structlog
from contextlib import asynccontextmanager
import asyncio

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'opal_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'opal_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'opal_active_connections',
    'Number of active connections'
)

AGENT_EXECUTION_TIME = Histogram(
    'opal_agent_execution_seconds',
    'Agent execution time in seconds',
    ['agent_name']
)

AGENT_SUCCESS_RATE = Counter(
    'opal_agent_executions_total',
    'Total agent executions',
    ['agent_name', 'status']
)

RETRIEVAL_OPERATIONS = Counter(
    'opal_retrieval_operations_total',
    'Total retrieval operations',
    ['operation_type', 'status']
)

VERIFICATION_RESULTS = Counter(
    'opal_verification_results_total',
    'Verification results',
    ['check_type', 'result']
)

BILLING_OPERATIONS = Counter(
    'opal_billing_operations_total',
    'Billing operations',
    ['operation_type', 'status']
)

DATABASE_OPERATIONS = Histogram(
    'opal_database_operation_duration_seconds',
    'Database operation duration',
    ['operation_type']
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Track active connections
        ACTIVE_CONNECTIONS.inc()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            method = request.method
            endpoint = self._get_endpoint_pattern(request)
            status_code = str(response.status_code)
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # Log slow requests
            if duration > 5.0:  # 5 seconds threshold
                log.warning("slow_request",
                          method=method,
                          endpoint=endpoint,
                          duration=duration,
                          status_code=status_code)
            
            return response
            
        except Exception as e:
            # Record error
            duration = time.time() - start_time
            method = request.method
            endpoint = self._get_endpoint_pattern(request)
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code="500"
            ).inc()
            
            log.error("request_error",
                     method=method,
                     endpoint=endpoint,
                     duration=duration,
                     error=str(e))
            
            raise
            
        finally:
            ACTIVE_CONNECTIONS.dec()
    
    def _get_endpoint_pattern(self, request: Request) -> str:
        """Extract endpoint pattern for metrics grouping"""
        path = request.url.path
        
        # Normalize paths with IDs
        import re
        
        # Replace UUIDs with placeholder
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path)
        
        # Replace other numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        return path


class PerformanceMonitor:
    """Monitor performance of various operations"""
    
    @staticmethod
    def track_agent_execution(agent_name: str):
        """Decorator to track agent execution metrics"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    status = "error"
                    log.error("agent_execution_error",
                             agent_name=agent_name,
                             error=str(e))
                    raise
                finally:
                    duration = time.time() - start_time
                    
                    AGENT_EXECUTION_TIME.labels(
                        agent_name=agent_name
                    ).observe(duration)
                    
                    AGENT_SUCCESS_RATE.labels(
                        agent_name=agent_name,
                        status=status
                    ).inc()
                    
                    log.info("agent_execution_complete",
                            agent_name=agent_name,
                            duration=duration,
                            status=status)
            
            return wrapper
        return decorator
    
    @staticmethod
    def track_retrieval_operation(operation_type: str):
        """Decorator to track retrieval operations"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                status = "success"
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    status = "error"
                    log.error("retrieval_operation_error",
                             operation_type=operation_type,
                             error=str(e))
                    raise
                finally:
                    RETRIEVAL_OPERATIONS.labels(
                        operation_type=operation_type,
                        status=status
                    ).inc()
            
            return wrapper
        return decorator
    
    @staticmethod
    def track_verification_result(check_type: str, result: bool):
        """Track verification check results"""
        VERIFICATION_RESULTS.labels(
            check_type=check_type,
            result="pass" if result else "fail"
        ).inc()
    
    @staticmethod
    def track_billing_operation(operation_type: str, success: bool):
        """Track billing operations"""
        BILLING_OPERATIONS.labels(
            operation_type=operation_type,
            status="success" if success else "error"
        ).inc()
    
    @staticmethod
    @asynccontextmanager
    async def track_database_operation(operation_type: str):
        """Context manager to track database operations"""
        start_time = time.time()
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            DATABASE_OPERATIONS.labels(
                operation_type=operation_type
            ).observe(duration)
            
            # Log slow database operations
            if duration > 2.0:  # 2 seconds threshold
                log.warning("slow_database_operation",
                          operation_type=operation_type,
                          duration=duration)


class HealthChecker:
    """Health check system for various components"""
    
    def __init__(self):
        self.components = {}
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            from app.db.session import SessionLocal
            from sqlalchemy import text
            
            start_time = time.time()
            
            async with SessionLocal() as session:
                # Simple connectivity test
                await session.execute(text("SELECT 1"))
                
                # Check for long-running queries
                result = await session.execute(text("""
                    SELECT COUNT(*) 
                    FROM pg_stat_activity 
                    WHERE state = 'active' 
                    AND query_start < NOW() - INTERVAL '30 seconds'
                    AND query != '<IDLE>'
                """))
                
                long_running_queries = result.scalar() or 0
            
            response_time = time.time() - start_time
            
            status = "healthy" if response_time < 1.0 and long_running_queries < 5 else "degraded"
            
            return {
                "status": status,
                "response_time_ms": response_time * 1000,
                "long_running_queries": long_running_queries,
                "timestamp": time.time()
            }
            
        except Exception as e:
            log.error("database_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def check_qdrant_health(self) -> Dict[str, Any]:
        """Check Qdrant vector database health"""
        try:
            from app.retrieval.qdrant_client import get_qdrant
            
            start_time = time.time()
            
            # Check collection status
            qdrant_client = get_qdrant()
            collections = qdrant_client.get_collections()
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response_time < 2.0 else "degraded",
                "response_time_ms": response_time * 1000,
                "collections_count": len(collections.collections),
                "timestamp": time.time()
            }
            
        except Exception as e:
            log.error("qdrant_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            from app.core.rate_limit import get_redis
            
            start_time = time.time()
            
            redis_client = get_redis()
            redis_client.ping()
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response_time < 0.5 else "degraded",
                "response_time_ms": response_time * 1000,
                "timestamp": time.time()
            }
            
        except Exception as e:
            log.error("redis_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def check_openai_health(self) -> Dict[str, Any]:
        """Check OpenAI API health"""
        try:
            from openai import OpenAI
            from app.core.config import get_settings
            
            settings = get_settings()
            if not settings.OPENAI_API_KEY:
                return {
                    "status": "unconfigured",
                    "error": "OpenAI API key not configured",
                    "timestamp": time.time()
                }
            
            start_time = time.time()
            
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Test with a minimal embedding request
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input="test"
            )
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response_time < 3.0 else "degraded",
                "response_time_ms": response_time * 1000,
                "model_available": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            log.error("openai_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def check_supabase_health(self) -> Dict[str, Any]:
        """Check Supabase storage health"""
        try:
            from app.storage.supabase_client import get_supabase
            
            start_time = time.time()
            
            sb = get_supabase()
            # Test storage connectivity
            buckets = sb.storage.list_buckets()
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response_time < 2.0 else "degraded",
                "response_time_ms": response_time * 1000,
                "buckets_count": len(buckets),
                "timestamp": time.time()
            }
            
        except Exception as e:
            log.error("supabase_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get health status of all components"""
        health_checks = {
            "database": await self.check_database_health(),
            "qdrant": await self.check_qdrant_health(),
            "redis": await self.check_redis_health(),
            "openai": await self.check_openai_health(),
            "supabase": await self.check_supabase_health()
        }
        
        # Determine overall status
        statuses = [check["status"] for check in health_checks.values()]
        
        if all(status == "healthy" for status in statuses):
            overall_status = "healthy"
        elif any(status == "unhealthy" for status in statuses):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "components": health_checks,
            "timestamp": time.time()
        }


class ErrorTracker:
    """Track and analyze errors for monitoring"""
    
    def __init__(self):
        self.error_counts = {}
        self.recent_errors = []
        self.max_recent_errors = 100
    
    def track_error(self, error_type: str, error_message: str, 
                   context: Optional[Dict[str, Any]] = None):
        """Track an error occurrence"""
        
        # Update error counts
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Store recent error
        error_info = {
            "type": error_type,
            "message": error_message,
            "context": context or {},
            "timestamp": time.time()
        }
        
        self.recent_errors.append(error_info)
        
        # Keep only recent errors
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors = self.recent_errors[-self.max_recent_errors:]
        
        # Log error
        log.error("error_tracked",
                 error_type=error_type,
                 error_message=error_message,
                 context=context)
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours"""
        
        cutoff_time = time.time() - (hours * 3600)
        recent_errors = [
            err for err in self.recent_errors 
            if err["timestamp"] > cutoff_time
        ]
        
        # Count by type
        error_counts = {}
        for err in recent_errors:
            error_counts[err["type"]] = error_counts.get(err["type"], 0) + 1
        
        return {
            "period_hours": hours,
            "total_errors": len(recent_errors),
            "error_types": error_counts,
            "recent_errors": recent_errors[-10:],  # Last 10 errors
            "timestamp": time.time()
        }


# Global instances
performance_monitor = PerformanceMonitor()
health_checker = HealthChecker()
error_tracker = ErrorTracker()


def get_metrics() -> str:
    """Get Prometheus metrics"""
    return generate_latest()


async def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status"""
    return await health_checker.get_comprehensive_health()


def track_error(error_type: str, error_message: str, 
               context: Optional[Dict[str, Any]] = None):
    """Track an error for monitoring"""
    error_tracker.track_error(error_type, error_message, context)


async def get_error_summary(hours: int = 24) -> Dict[str, Any]:
    """Get error summary"""
    return error_tracker.get_error_summary(hours)
