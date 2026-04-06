"""Redis-backed rate limiting dependency for FastAPI.

Uses a sliding window counter (INCR + EXPIRE) keyed by identifier and
endpoint group. The identifier is the authenticated user's ID when
available, otherwise the client IP address.
"""

from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.core.config import settings

_redis: Redis | None = None


async def get_redis() -> Redis:
    """Return a shared async Redis client, creating it on first call."""
    global _redis  # noqa: PLW0603
    if _redis is None:
        _redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )
    return _redis


def _get_identifier(request: Request) -> str:
    """Extract rate-limit identifier from the request.

    Uses the authenticated user ID from ``request.state.user_id`` when
    present (set by auth dependencies), otherwise falls back to the
    client IP address.
    """
    user_id = getattr(request.state, "user_id", None)
    if user_id is not None:
        return f"user:{user_id}"
    return f"ip:{request.client.host}" if request.client else "ip:unknown"


def rate_limit(
    max_requests: int = 60,
    window_seconds: int = 60,
) -> Callable:
    """Dependency factory that enforces per-caller rate limits.

    Parameters
    ----------
    max_requests:
        Maximum number of requests allowed within *window_seconds*.
    window_seconds:
        Length of the sliding window in seconds.

    Returns
    -------
    An async FastAPI dependency function.
    """

    async def _rate_limit_dependency(
        request: Request,
        redis: Redis = Depends(get_redis),
    ) -> None:
        identifier = _get_identifier(request)
        # Derive a stable endpoint-group name from the route path
        endpoint = request.scope.get("path", "unknown")
        key = f"rate_limit:{identifier}:{endpoint}"

        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, window_seconds)

        if current > max_requests:
            ttl = await redis.ttl(key)
            retry_after = max(ttl, 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

    return _rate_limit_dependency
