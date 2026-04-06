# 2. Adopt FastAPI + MVC + RIRO Architecture

Date: 2026-04-06

## Status

Proposed

## Context

We need a backend architecture that is:
- Easy for new developers to follow (clear conventions, predictable file locations)
- Maintainable as the feature count grows (isolated modules, not a monolithic router file)
- Compatible with async database operations (PostgreSQL + SQLAlchemy 2.0)
- Self-documenting through consistent naming (schemas tell you what goes in and what comes out)

We evaluated:
- **Flat structure** (all routes in one file) — doesn't scale past 10 endpoints
- **Domain-driven design** — too heavyweight for this project size
- **Feature-based MVC** — each feature is self-contained with router/service/crud/model/schema layers

## Decision

We adopt a **feature-based MVC architecture** with the **RIRO (Request In, Response Out) schema pattern**.

### Directory Structure

```
app/
├── main.py                          # FastAPI app, router registration, middleware
├── core/                            # Application-wide configuration
│   ├── config.py                    # Pydantic Settings (env vars, database URL)
│   └── security.py                  # JWT, password hashing, auth dependencies
├── common/                          # Shared base classes and utilities
│   ├── database.py                  # Async engine, session factory, get_db dependency
│   ├── models.py                    # Base, TimestampMixin
│   └── crud.py                      # GenericCRUD[ModelType] base class
└── features/                        # One directory per feature
    └── {feature_name}/
        ├── __init__.py
        ├── models.py                # SQLAlchemy models
        ├── schemas.py               # Pydantic schemas (RIRO pattern)
        ├── crud.py                  # Feature-specific CRUD (extends GenericCRUD)
        ├── service.py               # Business logic
        └── router.py                # FastAPI endpoints
```

### Layer Responsibilities

| Layer | File | Knows about | Does NOT know about |
|---|---|---|---|
| **Router** | router.py | Schemas, Service, FastAPI deps | SQLAlchemy models, database sessions directly |
| **Service** | service.py | CRUD, Schemas, business rules | FastAPI (no Request/Response objects) |
| **CRUD** | crud.py | Models, database session | Business rules, HTTP concerns |
| **Model** | models.py | SQLAlchemy, Base, mixins | Pydantic, FastAPI |
| **Schema** | schemas.py | Pydantic, Python types | SQLAlchemy, database |

Data flows one direction: **Router → Service → CRUD → Database**

### RIRO Schema Pattern

Every feature's schemas.py follows Request In, Response Out naming:

```python
# schemas.py

# Request schemas — what the client sends
class UserCreate(BaseModel):       # POST body
    email: str
    password: str
    name: str

class UserUpdate(BaseModel):       # PATCH body
    name: str | None = None
    email: str | None = None

# Response schemas — what the API returns
class UserResponse(BaseModel):     # Single item
    id: int
    email: str
    name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserListResponse(BaseModel): # List/paginated
    items: list[UserResponse]
    total: int
```

Naming convention:
- `{Entity}Create` — POST request body
- `{Entity}Update` — PATCH/PUT request body
- `{Entity}Response` — single item response
- `{Entity}ListResponse` — list/paginated response
- `{Entity}Filter` — query parameters for filtering (optional)

### Base Classes

**TimestampMixin** — every model gets created_at/updated_at:
```python
class TimestampMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
```

**GenericCRUD[T]** — async CRUD operations every feature inherits:
```python
class GenericCRUD(Generic[ModelType]):
    async def get(self, db, id) -> ModelType | None
    async def get_multi(self, db, skip, limit) -> list[ModelType]
    async def create(self, db, obj_in) -> ModelType
    async def update(self, db, db_obj, obj_in) -> ModelType
    async def delete(self, db, id) -> ModelType | None
```

### Router Registration

All routers are registered in main.py with consistent prefixes:
```python
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
```

Convention: `/api/v1/{feature_name_plural}`

### Database

- **PostgreSQL** via async SQLAlchemy 2.0 + asyncpg
- **Alembic** for migrations (autogenerate from models)
- **Session management** via FastAPI dependency injection (`get_db`)
- Connection pooling with pre-ping validation

## Consequences

**Easier:**
- Adding a new feature: copy the directory structure, implement each layer
- Finding code: feature name → directory → specific layer file
- Code review: changes are scoped to one feature directory
- Testing: each layer can be tested independently

**Harder:**
- Cross-feature logic requires a shared service or event system
- More files per feature (5-6 files even for simple features)
- Must maintain consistency across features (solved by CLAUDE.md + skills)

**Trade-offs:**
- We accept the overhead of 5-6 files per feature in exchange for predictable structure
- We accept async complexity in exchange for better performance under load
- We use generic CRUD base class but allow features to override for custom queries
