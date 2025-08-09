from __future__ import annotations

import traceback
from typing import Dict, Any, Optional, Type, Union
import structlog
from functools import wraps
from contextlib import asynccontextmanager

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.core.monitoring import track_error

log = structlog.get_logger()


class OpalError(Exception):
    """Base exception class for OPAL-specific errors"""
    
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(OpalError):
    """Input validation errors"""
    pass


class AuthenticationError(OpalError):
    """Authentication and authorization errors"""
    pass


class RateLimitError(OpalError):
    """Rate limiting errors"""
    pass


class InsufficientCreditsError(OpalError):
    """Billing and credit errors"""
    pass


class ProcessingError(OpalError):
    """Document processing and OCR errors"""
    pass


class RetrievalError(OpalError):
    """Retrieval and search errors"""
    pass


class AgentError(OpalError):
    """Agent execution errors"""
    pass


class VerificationError(OpalError):
    """Verification and validation errors"""
    pass


class ExportError(OpalError):
    """Export generation errors"""
    pass


class StorageError(OpalError):
    """Storage and file operation errors"""
    pass


class DatabaseError(OpalError):
    """Database operation errors"""
    pass


class ExternalServiceError(OpalError):
    """External service integration errors"""
    pass


class ErrorHandler:
    """Centralized error handling and recovery"""
    
    @staticmethod
    def handle_database_error(error: Exception, operation: str) -> HTTPException:
        """Handle database-related errors"""
        
        error_message = str(error)
        
        # Check for specific database errors
        if "connection" in error_message.lower():
            track_error("database_connection", error_message, {"operation": operation})
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database temporarily unavailable. Please try again later."
            )
        
        elif "timeout" in error_message.lower():
            track_error("database_timeout", error_message, {"operation": operation})
            return HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Database operation timed out. Please try again."
            )
        
        elif "constraint" in error_message.lower():
            track_error("database_constraint", error_message, {"operation": operation})
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data validation failed. Please check your input."
            )
        
        else:
            track_error("database_general", error_message, {"operation": operation})
            log.error("database_error", operation=operation, error=error_message)
            return HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed. Please contact support if this persists."
            )
    
    @staticmethod
    def handle_external_service_error(error: Exception, service: str) -> HTTPException:
        """Handle external service errors (OpenAI, Supabase, etc.)"""
        
        error_message = str(error)
        
        if service == "openai":
            if "rate_limit" in error_message.lower():
                track_error("openai_rate_limit", error_message, {"service": service})
                return HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="AI service rate limit reached. Please try again in a moment."
                )
            
            elif "quota" in error_message.lower():
                track_error("openai_quota", error_message, {"service": service})
                return HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service quota exceeded. Please contact support."
                )
            
            else:
                track_error("openai_general", error_message, {"service": service})
                return HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="AI service temporarily unavailable. Please try again."
                )
        
        elif service == "supabase":
            track_error("supabase_error", error_message, {"service": service})
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Storage service temporarily unavailable. Please try again."
            )
        
        else:
            track_error("external_service_error", error_message, {"service": service})
            return HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"External service ({service}) error. Please try again."
            )
    
    @staticmethod
    def handle_validation_error(error: Union[ValidationError, ValueError]) -> HTTPException:
        """Handle input validation errors"""
        
        error_message = str(error)
        
        if isinstance(error, ValidationError):
            track_error("validation_error", error_message, error.details)
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error.message
            )
        else:
            track_error("value_error", error_message)
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input provided. Please check your data."
            )
    
    @staticmethod
    def handle_processing_error(error: Exception, operation: str) -> HTTPException:
        """Handle document processing and OCR errors"""
        
        error_message = str(error)
        
        if "timeout" in error_message.lower():
            track_error("processing_timeout", error_message, {"operation": operation})
            return HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Processing timed out. Please try with a smaller document."
            )
        
        elif "memory" in error_message.lower():
            track_error("processing_memory", error_message, {"operation": operation})
            return HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Document too large to process. Please try a smaller file."
            )
        
        else:
            track_error("processing_error", error_message, {"operation": operation})
            return HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Document processing failed. Please check file format and try again."
            )
    
    @staticmethod
    def handle_agent_error(error: Exception, agent_name: str) -> HTTPException:
        """Handle agent execution errors"""
        
        error_message = str(error)
        
        track_error("agent_error", error_message, {"agent": agent_name})
        
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis engine ({agent_name}) encountered an error. Our team has been notified."
        )
    
    @staticmethod
    def handle_generic_error(error: Exception, operation: str = "unknown") -> HTTPException:
        """Handle generic/unexpected errors"""
        
        error_message = str(error)
        error_type = type(error).__name__
        
        track_error("generic_error", error_message, {
            "error_type": error_type,
            "operation": operation,
            "traceback": traceback.format_exc()
        })
        
        log.error("unexpected_error",
                 error_type=error_type,
                 error_message=error_message,
                 operation=operation)
        
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Our team has been notified."
        )


def safe_async_operation(operation_name: str, error_handler: Optional[callable] = None):
    """Decorator for safe async operations with error handling"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except OpalError as e:
                # Handle known OPAL errors
                track_error(e.error_code, e.message, e.details)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=e.message
                )
            except HTTPException:
                # Re-raise HTTP exceptions
                raise
            except Exception as e:
                # Handle unexpected errors
                if error_handler:
                    raise error_handler(e, operation_name)
                else:
                    raise ErrorHandler.handle_generic_error(e, operation_name)
        
        return wrapper
    return decorator


@asynccontextmanager
async def error_context(operation: str, error_handler: Optional[callable] = None):
    """Context manager for error handling"""
    
    try:
        yield
    except OpalError as e:
        track_error(e.error_code, e.message, e.details)
        log.error("opal_error", 
                 operation=operation,
                 error_code=e.error_code,
                 message=e.message,
                 details=e.details)
        raise
    except Exception as e:
        if error_handler:
            raise error_handler(e, operation)
        else:
            raise ErrorHandler.handle_generic_error(e, operation)


class GlobalExceptionHandler:
    """Global exception handler for FastAPI"""
    
    @staticmethod
    async def handle_validation_exception(request: Request, exc: ValueError):
        """Handle validation exceptions"""
        error_response = ErrorHandler.handle_validation_error(exc)
        return JSONResponse(
            status_code=error_response.status_code,
            content={"detail": error_response.detail}
        )
    
    @staticmethod
    async def handle_opal_exception(request: Request, exc: OpalError):
        """Handle OPAL-specific exceptions"""
        track_error(exc.error_code, exc.message, exc.details)
        
        # Map error types to HTTP status codes
        status_code_map = {
            ValidationError: status.HTTP_400_BAD_REQUEST,
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
            InsufficientCreditsError: status.HTTP_402_PAYMENT_REQUIRED,
            ProcessingError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            RetrievalError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            AgentError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            VerificationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            ExportError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            StorageError: status.HTTP_503_SERVICE_UNAVAILABLE,
            DatabaseError: status.HTTP_503_SERVICE_UNAVAILABLE,
            ExternalServiceError: status.HTTP_502_BAD_GATEWAY
        }
        
        status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return JSONResponse(
            status_code=status_code,
            content={
                "detail": exc.message,
                "error_code": exc.error_code,
                "details": exc.details
            }
        )
    
    @staticmethod
    async def handle_generic_exception(request: Request, exc: Exception):
        """Handle generic exceptions"""
        error_response = ErrorHandler.handle_generic_error(exc, "global_handler")
        return JSONResponse(
            status_code=error_response.status_code,
            content={"detail": error_response.detail}
        )


# Utility functions for common error scenarios
def validate_uuid(value: str, field_name: str = "id") -> str:
    """Validate UUID format"""
    import uuid
    
    try:
        uuid.UUID(value)
        return value
    except ValueError:
        raise ValidationError(
            f"Invalid {field_name} format",
            "invalid_uuid",
            {"field": field_name, "value": value}
        )


def validate_file_size(size: int, max_size: int, filename: str = "file") -> None:
    """Validate file size"""
    if size > max_size:
        raise ValidationError(
            f"File {filename} exceeds maximum size limit",
            "file_too_large",
            {"filename": filename, "size": size, "max_size": max_size}
        )


def validate_credits_balance(required: int, available: int) -> None:
    """Validate sufficient credits"""
    if available < required:
        raise InsufficientCreditsError(
            f"Insufficient credits. Required: {required}, Available: {available}",
            "insufficient_credits",
            {"required": required, "available": available, "shortfall": required - available}
        )


def validate_rate_limit(current_count: int, limit: int, window: str) -> None:
    """Validate rate limits"""
    if current_count >= limit:
        raise RateLimitError(
            f"Rate limit exceeded. Maximum {limit} requests per {window}",
            "rate_limit_exceeded",
            {"current": current_count, "limit": limit, "window": window}
        )
