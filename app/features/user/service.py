import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password

from . import crud, schemas
from .models import User


async def create_user(db: AsyncSession, user_in: schemas.UserCreate) -> User:
    obj_in = user_in.model_dump(exclude={"password"})
    obj_in["hashed_password"] = hash_password(user_in.password)
    return await crud.user.create(db, obj_in=obj_in)


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    return await crud.user.get_by_email(db, email=email)


async def get_user(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await crud.user.get(db, user_id)


async def list_users(
    db: AsyncSession, skip: int = 0, limit: int = 20
) -> schemas.UserListResponse:
    items = await crud.user.get_multi(db, skip=skip, limit=limit)
    total = await crud.user.count(db)
    return schemas.UserListResponse(items=items, total=total)


async def update_user(
    db: AsyncSession, db_obj: User, user_in: schemas.UserUpdate
) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    return await crud.user.update(db, db_obj=db_obj, obj_in=update_data)


async def soft_delete_user(db: AsyncSession, db_obj: User) -> User:
    return await crud.user.update(db, db_obj=db_obj, obj_in={"is_active": False})
