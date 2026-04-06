import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.pagination import PaginationParams
from app.features.auth.dependencies import get_current_user
from app.features.user.models import User

from . import schemas, service

router = APIRouter()


@router.post(
    "/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED
)
async def create_category(
    category_in: schemas.CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_category(
        db, user_id=current_user.id, category_in=category_in
    )


@router.get("/", response_model=schemas.CategoryListResponse)
async def list_categories(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_categories(
        db, user_id=current_user.id, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/{category_id}", response_model=schemas.CategoryResponse)
async def get_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cat = await service.get_category(db, category_id=category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return cat


@router.patch("/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    category_in: schemas.CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cat = await service.get_category(db, category_id=category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return await service.update_category(db, db_obj=cat, category_in=category_in)


@router.delete("/{category_id}", response_model=schemas.CategoryResponse)
async def delete_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cat = await service.get_category(db, category_id=category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return await service.delete_category(db, category_id=category_id)
