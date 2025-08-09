from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, HTTPException, status
import redis

from app.core.config import get_settings


def get_redis() -> redis.Redis:
    return redis.from_url(get_settings().REDIS_URL)


def rate_limiter(max_per_day: int = 30) -> Callable:
    r = get_redis()

    async def _middleware(request: Request, call_next):
        user = getattr(request.state, "user", None)
        if not user:
            return await call_next(request)
        key = f"rate:{user['id']}:{time.strftime('%Y-%m-%d')}"
        val = r.incr(key)
        if val == 1:
            r.expire(key, 86400)
        if val > max_per_day:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
        return await call_next(request)

    return _middleware


