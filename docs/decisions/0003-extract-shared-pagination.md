# 3. Extract Shared Pagination Parameters

Date: 2026-04-06

## Status

Proposed

## Context

Both `user/router.py` and `todo/router.py` duplicate the same pagination pattern:

```python
skip: int = Query(0, ge=0),
limit: int = Query(20, ge=1, le=100),
```

With 2 features this is manageable. With 10+ features, changing the default page size or max limit requires editing every router. This violates DRY and creates inconsistency risk.

## Decision

Extract pagination into `app/common/pagination.py` as a dataclass + FastAPI `Depends()`:

```python
@dataclass
class PaginationParams:
    skip: int = Query(0, ge=0)
    limit: int = Query(20, ge=1, le=100)
```

Routers use it as: `pagination: PaginationParams = Depends()`

## Consequences

- One place to change pagination defaults and validation
- Consistent behavior across all features
- Slightly more indirection in router signatures (trade-off accepted)
- Zero behavior change — same defaults, same query param names
