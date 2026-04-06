import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .models import Category


async def create_category(
    db: AsyncSession, user_id: uuid.UUID, category_in: schemas.CategoryCreate
) -> Category:
    data = category_in.model_dump()
    data["user_id"] = user_id
    return await crud.category.create(db, obj_in=data)


async def list_categories(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
) -> schemas.CategoryListResponse:
    items = await crud.category.get_by_user(db, user_id, skip=skip, limit=limit)
    total = await crud.category.count_by_user(db, user_id)
    return schemas.CategoryListResponse(items=items, total=total)


async def get_category(db: AsyncSession, category_id: uuid.UUID) -> Category | None:
    return await crud.category.get(db, category_id)


async def update_category(
    db: AsyncSession, db_obj: Category, category_in: schemas.CategoryUpdate
) -> Category:
    update_data = category_in.model_dump(exclude_unset=True)
    return await crud.category.update(db, db_obj=db_obj, obj_in=update_data)


async def delete_category(db: AsyncSession, category_id: uuid.UUID) -> Category | None:
    return await crud.category.delete(db, id=category_id)
