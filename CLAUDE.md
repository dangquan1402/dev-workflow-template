# Dev Workflow Template

A doc-first development workflow with branch-type-specific pipelines.

## Branch Types & Conventions

| Prefix | Purpose | Branches from | Merges to |
|---|---|---|---|
| `feature/*` | New functionality | `develop` | `develop` |
| `bugfix/*` | Fix broken behavior | `develop` | `develop` |
| `hotfix/*` | Urgent production fix | `main` | `main` + `develop` |
| `refactor/*` | Restructure, no behavior change | `develop` | `develop` |
| `chore/*` | Deps, CI, tooling | `develop` | `develop` |

Branch naming: `{type}/GH-{issue_number}-{short-description}`
Example: `feature/GH-42-user-auth`

## Commit Convention

Use Conventional Commits:
- `feat(scope): description` — new feature (MINOR bump)
- `fix(scope): description` — bug fix (PATCH bump)
- `refactor(scope): description` — restructure (no bump)
- `chore(scope): description` — maintenance (no bump)
- `docs(scope): description` — documentation only (no bump)
- Add `BREAKING CHANGE:` footer for breaking changes (MAJOR bump)

## Doc-First Rules

### Features (full pipeline)
1. Write ADR in `docs/decisions/` if architectural
2. Update ERD in `docs/reference/erd.md` if new tables
3. Define API contract in `docs/reference/api/` before coding
4. Implement code following base class conventions
5. Update docs in the SAME PR as code — never a follow-up

### Bugfixes (diagnosis-first)
1. Write regression test FIRST (proves the bug exists)
2. Fix with minimal change — no refactoring
3. Document root cause in PR description
4. Update docs ONLY if behavior changed

### Hotfixes (ship first, document after)
1. Minimal patch, smallest possible change
2. Smoke test passes
3. Post-mortem ADR within 48 hours after merge
4. Follow-up issue for deeper fix if needed

### Refactors (prove no behavior change)
1. Write ADR justifying WHY (not "cleaner" — concrete reason)
2. ALL existing tests must pass — zero behavior change
3. No new features smuggled in
4. API contracts unchanged, ERD unchanged
5. Update internal docs only (architecture, CLAUDE.md)

### Chores (lightweight)
1. Tests pass
2. Note CVE number if security-related dependency update
3. No changelog unless breaking

## Documentation Structure (Diátaxis)

```
docs/
  tutorials/       — learning-oriented, step-by-step
  how-to/          — goal-oriented, solve a specific problem
  reference/       — factual, mirrors codebase structure
    api/           — API contracts (OpenAPI or markdown)
    erd.md         — entity-relationship diagram
  explanation/     — understanding-oriented, architecture context
  decisions/       — ADRs (immutable, numbered)
```

## Review Requirements

| Branch type | Reviewers | Doc review? |
|---|---|---|
| `feature/*` | 2 | Yes |
| `bugfix/*` | 1 | Only if behavior changed |
| `hotfix/*` | 1 (senior) | No (post-mortem after) |
| `refactor/*` | 2 | Architecture docs only |
| `chore/*` | 1 | No |

## Backend Architecture

### Directory Layout
```
app/
├── main.py                      # Router registration + health endpoint
├── core/
│   ├── config.py                # Pydantic Settings (DATABASE_URL, SECRET_KEY, REDIS)
│   └── security.py              # JWT + bcrypt
├── common/
│   ├── database.py              # async engine, session, get_db dependency
│   ├── models.py                # TimestampMixin (created_at, updated_at)
│   ├── crud.py                  # GenericCRUD[T] base class
│   └── pagination.py            # PaginationParams (skip, limit)
└── features/{feature_name}/     # One directory per feature
    ├── models.py                # SQLAlchemy model
    ├── schemas.py               # RIRO Pydantic schemas
    ├── crud.py                  # Extends GenericCRUD
    ├── service.py               # Business logic
    └── router.py                # FastAPI endpoints
```

### DO NOT scan the repo to understand patterns. Use these templates directly.

### Feature File Templates

**models.py:**
```python
from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.database import Base
from app.common.models import TimestampMixin

class {Entity}(TimestampMixin, Base):
    __tablename__ = "{table_name_plural}"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # add columns here
```

**schemas.py (RIRO pattern):**
```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class {Entity}Create(BaseModel):
    """POST request body"""
    # fields the client sends

class {Entity}Update(BaseModel):
    """PATCH request body — all fields optional"""
    # fields with | None = None

class {Entity}Response(BaseModel):
    """Single item response"""
    id: int
    # all readable fields
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class {Entity}ListResponse(BaseModel):
    """Paginated list response"""
    items: list[{Entity}Response]
    total: int
```

**crud.py:**
```python
from app.common.crud import GenericCRUD
from .models import {Entity}

class {Entity}CRUD(GenericCRUD[{Entity}]):
    # add custom queries here (get_by_field, get_filtered, etc.)
    pass

{entity} = {Entity}CRUD({Entity})
```

**service.py:**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud, schemas
from .models import {Entity}

async def create_{entity}(db: AsyncSession, obj_in: schemas.{Entity}Create) -> {Entity}:
    return await crud.{entity}.create(db, obj_in=obj_in.model_dump())

async def get_{entity}(db: AsyncSession, id: int) -> {Entity} | None:
    return await crud.{entity}.get(db, id)

async def list_{entities}(db: AsyncSession, skip: int = 0, limit: int = 20) -> schemas.{Entity}ListResponse:
    items = await crud.{entity}.get_multi(db, skip=skip, limit=limit)
    total = await crud.{entity}.count(db)
    return schemas.{Entity}ListResponse(items=items, total=total)
```

**router.py:**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.database import get_db
from app.common.pagination import PaginationParams
from . import schemas, service

router = APIRouter()

@router.post("/", response_model=schemas.{Entity}Response, status_code=status.HTTP_201_CREATED)
async def create_{entity}(obj_in: schemas.{Entity}Create, db: AsyncSession = Depends(get_db)):
    return await service.create_{entity}(db, obj_in=obj_in)

@router.get("/", response_model=schemas.{Entity}ListResponse)
async def list_{entities}(pagination: PaginationParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await service.list_{entities}(db, skip=pagination.skip, limit=pagination.limit)

@router.get("/{id}", response_model=schemas.{Entity}Response)
async def get_{entity}(id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.get_{entity}(db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="{Entity} not found")
    return obj
```

**Register in app/main.py:**
```python
from app.features.{feature_name}.router import router as {feature_name}_router
app.include_router({feature_name}_router, prefix="/api/v1/{feature_name_plural}", tags=["{feature_name_plural}"])
```

**Register model in alembic/env.py:**
```python
from app.features.{feature_name}.models import {Entity}  # noqa: F401
```

### GenericCRUD Methods (already available — do not rewrite)

- `get(db, id)` → single item or None
- `get_multi(db, skip, limit)` → list
- `count(db)` → int
- `create(db, obj_in=dict)` → created item
- `update(db, db_obj=item, obj_in=dict)` → updated item
- `delete(db, id=id)` → deleted item or None

### Naming Rules

| Thing | Convention | Example |
|---|---|---|
| Feature dir | snake_case | `document_processor` |
| Table name | snake_case, plural | `users`, `todos` |
| Model class | PascalCase, singular | `User`, `Todo` |
| Schema | PascalCase + suffix | `UserCreate`, `UserResponse` |
| CRUD instance | lowercase singular | `user = UserCRUD(User)` |
| API prefix | `/api/v1/{plural}` | `/api/v1/users` |

## Available Skills

- `/new-feature` — start a feature branch with full doc-first pipeline
- `/bugfix` — start a bugfix with diagnosis-first workflow
- `/hotfix` — start a hotfix with fast-track process
- `/refactor` — start a refactor with justification pipeline
- `/chore` — start a chore with lightweight workflow
