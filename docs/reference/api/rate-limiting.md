# Rate Limiting API Reference

## Overview

Redis-backed rate limiting applied as a FastAPI dependency on route handlers.
Uses a sliding window counter (INCR + EXPIRE) per identifier per endpoint group.

## Behavior

| Endpoint group | Max requests | Window | Identifier |
|---|---|---|---|
| Auth (`/api/v1/auth/*`) | 10 per minute | 60 seconds | IP address |
| Todos (`/api/v1/todos/*`) | 60 per minute | 60 seconds | User ID (authenticated) |

### Key pattern

```
rate_limit:{identifier}:{endpoint_group}
```

- **Authenticated requests**: `identifier` = user ID (from JWT)
- **Unauthenticated requests**: `identifier` = client IP address

### Rate limit exceeded response

**Status**: `429 Too Many Requests`

```json
{
  "detail": "Rate limit exceeded. Try again in {seconds} seconds."
}
```

**Headers**:

| Header | Description |
|---|---|
| `Retry-After` | Seconds until the rate limit window resets |

## Configuration

| Setting | Default | Description |
|---|---|---|
| `RATE_LIMIT_PER_MINUTE` | 60 | Default rate limit for authenticated endpoints |
| `RATE_LIMIT_AUTH_PER_MINUTE` | 10 | Stricter rate limit for auth endpoints (login, register) |
| `REDIS_HOST` | `redis` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |

## Implementation

The rate limiter is implemented as a dependency factory (`rate_limit()`) in
`app/common/rate_limit.py`. It returns an async callable suitable for use
with `Depends()` in FastAPI route decorators.

```python
from app.common.rate_limit import rate_limit

@router.post("/login", dependencies=[Depends(rate_limit(max_requests=10, window_seconds=60))])
async def login(...):
    ...
```
