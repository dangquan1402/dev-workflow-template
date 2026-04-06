from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.pagination import PaginationParams
from app.features.auth.dependencies import get_current_admin, get_current_user
from app.features.user.models import User, UserRole

from . import schemas, service

router = APIRouter()


@router.post(
    "/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await service.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await service.create_user(db, user_in=user_in)


@router.get("/", response_model=schemas.UserListResponse)
async def list_users(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return await service.list_users(db, skip=pagination.skip, limit=pagination.limit)


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only owner or admin can update
    if current_user.id != user_id and current_user.role != UserRole.admin.value:
        raise HTTPException(status_code=403, detail="Not allowed to update this user")

    # Only admin can change roles
    if user_in.role is not None and current_user.role != UserRole.admin.value:
        raise HTTPException(status_code=403, detail="Only admins can change roles")

    user = await service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_in.email:
        existing = await service.get_by_email(db, email=user_in.email)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email already taken")
    return await service.update_user(db, db_obj=user, user_in=user_in)


@router.delete("/{user_id}", response_model=schemas.UserResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user = await service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await service.soft_delete_user(db, db_obj=user)
