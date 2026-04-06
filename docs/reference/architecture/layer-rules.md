# Layer Rules

Each layer has strict boundaries. Do not cross them.

## router.py
- Defines FastAPI endpoints
- Receives request data via Pydantic schemas
- Calls **service** layer (never CRUD directly)
- Returns response schemas
- Handles HTTP concerns (status codes, HTTPException)
- Injects dependencies (`Depends(get_db)`, `Depends(get_current_user)`)

## service.py
- Contains business logic and orchestration
- Calls **CRUD** layer for database operations
- Does NOT import FastAPI (no Request, Response, HTTPException)
- Raises domain exceptions (not HTTP exceptions)
- Can call other feature services for cross-feature logic

## crud.py
- Extends `GenericCRUD` from `app/common/crud.py`
- Adds feature-specific queries
- Only knows about SQLAlchemy models and sessions
- Does NOT know about Pydantic schemas or business rules

## models.py
- SQLAlchemy ORM models
- Inherits from `Base` and `TimestampMixin`
- Defines table name, columns, relationships, indexes

## schemas.py (RIRO Pattern)
- Request In, Response Out
- `{Entity}Create` — POST body
- `{Entity}Update` — PATCH body (all fields optional)
- `{Entity}Response` — single item (with `model_config = ConfigDict(from_attributes=True)`)
- `{Entity}ListResponse` — `items: list[{Entity}Response]` + `total: int`

## Dependency Injection

Database session:
```python
db: AsyncSession = Depends(get_db)
```

Pagination (shared):
```python
from app.common.pagination import PaginationParams
pagination: PaginationParams = Depends()
# then use pagination.skip, pagination.limit
```

## GenericCRUD Methods (do not rewrite)

- `get(db, id)` → item or None
- `get_multi(db, skip, limit)` → list
- `count(db)` → int
- `create(db, obj_in=dict)` → created item
- `update(db, db_obj=item, obj_in=dict)` → updated item
- `delete(db, id=id)` → deleted item or None
