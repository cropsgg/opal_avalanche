"""
Authentication API endpoints for OPAL Server
Simple hardcoded authentication for demo purposes
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import structlog

log = structlog.get_logger()

router = APIRouter()
security = HTTPBearer()

# Hardcoded credentials
HARDCODED_USER_ID = "opalteam321"
HARDCODED_PASSWORD = "weareteamalphaq"

# In-memory session storage (for demo only)
active_sessions: dict[str, dict] = {}


class LoginRequest(BaseModel):
    """Login request model"""
    user_id: str
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # 1 hour
    user_id: str


class UserInfo(BaseModel):
    """User information model"""
    user_id: str
    authenticated: bool
    session_created: datetime


def create_access_token(user_id: str) -> str:
    """Create a new access token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    active_sessions[token] = {
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at
    }
    
    return token


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInfo:
    """Get current authenticated user"""
    token = credentials.credentials
    
    # Check if token exists and is valid
    if token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    session = active_sessions[token]
    
    # Check if token has expired
    if datetime.utcnow() > session["expires_at"]:
        del active_sessions[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserInfo(
        user_id=session["user_id"],
        authenticated=True,
        session_created=session["created_at"]
    )


# Optional dependency for protected routes
def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[UserInfo]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """
    Authenticate user with hardcoded credentials
    """
    log.info("auth.login.attempt", user_id=request.user_id)
    
    # Validate credentials
    if request.user_id != HARDCODED_USER_ID or request.password != HARDCODED_PASSWORD:
        log.warning("auth.login.failed", user_id=request.user_id, reason="invalid_credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID or password",
        )
    
    # Create access token
    access_token = create_access_token(request.user_id)
    
    log.info("auth.login.success", user_id=request.user_id)
    
    return LoginResponse(
        access_token=access_token,
        user_id=request.user_id
    )


@router.post("/logout")
async def logout(current_user: UserInfo = Depends(get_current_user)):
    """
    Logout current user by invalidating their token
    """
    # Find and remove the user's active session
    for token, session in list(active_sessions.items()):
        if session["user_id"] == current_user.user_id:
            del active_sessions[token]
            break
    
    log.info("auth.logout", user_id=current_user.user_id)
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: UserInfo = Depends(get_current_user)) -> UserInfo:
    """
    Get current user information
    """
    return current_user


@router.get("/status")
async def auth_status():
    """
    Get authentication system status
    """
    return {
        "auth_enabled": True,
        "active_sessions": len(active_sessions),
        "session_timeout": 3600  # seconds
    }


# Cleanup expired sessions periodically (called by main app)
def cleanup_expired_sessions():
    """Remove expired sessions from memory"""
    current_time = datetime.utcnow()
    expired_tokens = [
        token for token, session in active_sessions.items()
        if current_time > session["expires_at"]
    ]
    
    for token in expired_tokens:
        del active_sessions[token]
    
    if expired_tokens:
        log.info("auth.cleanup", expired_sessions=len(expired_tokens))
