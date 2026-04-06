# Code Templates

Copy-paste these when creating a new feature. Replace `{Entity}`, `{entity}`, `{feature_name}`, `{table_name_plural}`.

**DO NOT scan existing features for patterns. Use these templates.**

## models.py

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

## schemas.py

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class {Entity}Create(BaseModel):
    """POST request body"""
    # required fields

class {Entity}Update(BaseModel):
    """PATCH request body — all optional"""
    # fields with | None = None

class {Entity}Response(BaseModel):
    id: int
    # all readable fields
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class {Entity}ListResponse(BaseModel):
    items: list[{Entity}Response]
    total: int
```

## crud.py

```python
from app.common.crud import GenericCRUD
from .models import {Entity}

class {Entity}CRUD(GenericCRUD[{Entity}]):
    # add custom queries here
    pass

{entity} = {Entity}CRUD({Entity})
```

## service.py

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

## router.py

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

## Registration

In `app/main.py`:
```python
from app.features.{feature_name}.router import router as {feature_name}_router
app.include_router({feature_name}_router, prefix="/api/v1/{feature_name_plural}", tags=["{feature_name_plural}"])
```

In `alembic/env.py`:
```python
from app.features.{feature_name}.models import {Entity}  # noqa: F401
```
