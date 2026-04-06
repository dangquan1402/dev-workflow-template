# Architecture Conventions

## Feature Module Pattern

Every feature lives in `app/features/{feature_name}/` with these files:

```
app/features/{feature_name}/
├── __init__.py
├── models.py      # SQLAlchemy ORM models
├── schemas.py     # Pydantic RIRO schemas
├── crud.py        # Database operations (extends GenericCRUD)
├── service.py     # Business logic
└── router.py      # FastAPI endpoints
```

Not every feature needs all files. Minimum viable feature: `router.py` + `schemas.py`. Add `models.py` + `crud.py` when the feature touches the database. Add `service.py` when business logic is more than a CRUD call.

## Layer Rules

### router.py
- Defines FastAPI endpoints (`@router.get`, `@router.post`, etc.)
- Receives request data via Pydantic schemas
- Calls service layer (never CRUD directly)
- Returns response schemas
- Handles HTTP concerns (status codes, headers)
- Injects dependencies (`Depends(get_db)`, `Depends(get_current_user)`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.database import get_db
from . import schemas, service

router = APIRouter()

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await service.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await service.create_user(db, user_in=user_in)
```

### service.py
- Contains business logic and orchestration
- Calls CRUD layer for database operations
- Does NOT import FastAPI (no Request, Response, HTTPException)
- Raises domain exceptions (not HTTP exceptions)
- Can call other feature services for cross-feature logic

```python
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud, schemas

async def create_user(db: AsyncSession, user_in: schemas.UserCreate) -> models.User:
    hashed_password = hash_password(user_in.password)
    return await crud.user.create(db, obj_in={**user_in.model_dump(), "hashed_password": hashed_password})

async def get_by_email(db: AsyncSession, email: str) -> models.User | None:
    return await crud.user.get_by_field(db, field="email", value=email)
```

### crud.py
- Extends `GenericCRUD` from `app/common/crud.py`
- Adds feature-specific queries
- Only knows about SQLAlchemy models and sessions
- Does NOT know about Pydantic schemas or business rules

```python
from app.common.crud import GenericCRUD
from .models import User

class UserCRUD(GenericCRUD[User]):
    async def get_by_email(self, db, email: str) -> User | None:
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalar_one_or_none()

user = UserCRUD(User)
```

### models.py
- SQLAlchemy ORM models
- Inherits from `Base` and `TimestampMixin`
- Defines table name, columns, relationships, indexes
- Column naming: snake_case, matches database column names

```python
from sqlalchemy import Column, Integer, String
from app.common.models import Base, TimestampMixin

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
```

### schemas.py (RIRO Pattern)

Request In, Response Out. Four schema types per entity:

```python
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime

# --- Request schemas (what the client sends) ---

class UserCreate(BaseModel):
    """POST /users — create a new user"""
    email: EmailStr
    password: str
    name: str

class UserUpdate(BaseModel):
    """PATCH /users/{id} — update user fields"""
    name: str | None = None
    email: EmailStr | None = None

# --- Response schemas (what the API returns) ---

class UserResponse(BaseModel):
    """Single user response"""
    id: int
    email: str
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserListResponse(BaseModel):
    """Paginated user list"""
    items: list[UserResponse]
    total: int
```

Naming rules:
| Pattern | Purpose | Example |
|---|---|---|
| `{Entity}Create` | POST body | `UserCreate` |
| `{Entity}Update` | PATCH/PUT body | `UserUpdate` |
| `{Entity}Response` | Single item response | `UserResponse` |
| `{Entity}ListResponse` | List/paginated response | `UserListResponse` |
| `{Entity}Filter` | Query params for filtering | `UserFilter` |

## Dependency Injection

### Database session
```python
from app.common.database import get_db

@router.get("/")
async def list_items(db: AsyncSession = Depends(get_db)):
    ...
```

### Current user (authenticated endpoints)
```python
from app.core.security import get_current_user

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    ...
```

## Router Registration

In `app/main.py`, every feature router is registered with a versioned prefix:

```python
from app.features.user.router import router as user_router

app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
```

Convention:
- Prefix: `/api/v1/{feature_name_plural}`
- Tags: `["{feature_name_plural}"]` (groups endpoints in Swagger UI)

## Adding a New Feature

1. Create `app/features/{feature_name}/`
2. Define models in `models.py` (if database tables needed)
3. Define schemas in `schemas.py` (RIRO pattern)
4. Create CRUD in `crud.py` (extend GenericCRUD)
5. Write business logic in `service.py`
6. Define endpoints in `router.py`
7. Register router in `app/main.py`
8. Create Alembic migration: `alembic revision --autogenerate -m "add {feature_name} tables"`
9. Run migration: `alembic upgrade head`

Or use the Claude Code skill: `/new-feature`

## Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Feature directory | snake_case | `document_processor` |
| Table name | snake_case, plural | `users`, `ocr_pages` |
| Column name | snake_case | `created_at`, `hashed_password` |
| Model class | PascalCase, singular | `User`, `OcrPage` |
| Schema class | PascalCase + suffix | `UserCreate`, `UserResponse` |
| Router variable | `router` (in file), `{name}_router` (in main) | `user_router` |
| API prefix | `/api/v1/{plural}` | `/api/v1/users` |
| CRUD instance | lowercase, singular | `user = UserCRUD(User)` |
