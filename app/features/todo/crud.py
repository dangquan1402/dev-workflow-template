from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.crud import GenericCRUD
from app.features.category.models import Category, todo_categories
from app.features.user.models import User

from .models import Todo


class TodoCRUD(GenericCRUD[Todo]):
    async def get(self, db: AsyncSession, id: int) -> Todo | None:
        result = await db.execute(
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.categories))
        )
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: dict[str, Any]) -> Todo:
        category_ids = obj_in.pop("category_ids", [])
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()

        if category_ids:
            cats = await db.execute(
                select(Category).where(Category.id.in_(category_ids))
            )
            db_obj.categories = list(cats.scalars().all())
            await db.flush()

        await db.refresh(db_obj)
        # Eager load categories on the refreshed object
        result = await db.execute(
            select(self.model)
            .where(self.model.id == db_obj.id)
            .options(selectinload(self.model.categories))
        )
        return result.scalar_one()

    async def update(
        self, db: AsyncSession, *, db_obj: Todo, obj_in: dict[str, Any]
    ) -> Todo:
        category_ids = obj_in.pop("category_ids", None)
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)

        if category_ids is not None:
            cats = await db.execute(
                select(Category).where(Category.id.in_(category_ids))
            )
            db_obj.categories = list(cats.scalars().all())

        await db.flush()
        result = await db.execute(
            select(self.model)
            .where(self.model.id == db_obj.id)
            .options(selectinload(self.model.categories))
        )
        return result.scalar_one()

    async def get_by_user(
        self, db: AsyncSession, user_id: int, *, skip: int = 0, limit: int = 20
    ) -> list[Todo]:
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(selectinload(self.model.categories))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(
        self, db: AsyncSession, status: str, *, skip: int = 0, limit: int = 20
    ) -> list[Todo]:
        stmt = (
            select(self.model)
            .where(self.model.status == status)
            .options(selectinload(self.model.categories))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_filtered(
        self,
        db: AsyncSession,
        *,
        user_id: int | None = None,
        status: str | None = None,
        category_id: int | None = None,
        exclude_inactive_users: bool = True,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Todo]:
        stmt = select(self.model).options(selectinload(self.model.categories))
        if exclude_inactive_users:
            stmt = stmt.join(User, self.model.user_id == User.id).where(
                User.is_active.is_(True)
            )
        if user_id is not None:
            stmt = stmt.where(self.model.user_id == user_id)
        if status is not None:
            stmt = stmt.where(self.model.status == status)
        if category_id is not None:
            stmt = stmt.join(todo_categories).where(
                todo_categories.c.category_id == category_id
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        db: AsyncSession,
        *,
        user_id: int | None = None,
        status: str | None = None,
        category_id: int | None = None,
        exclude_inactive_users: bool = True,
    ) -> int:
        stmt = select(func.count()).select_from(self.model)
        if exclude_inactive_users:
            stmt = stmt.join(User, self.model.user_id == User.id).where(
                User.is_active.is_(True)
            )
        if user_id is not None:
            stmt = stmt.where(self.model.user_id == user_id)
        if status is not None:
            stmt = stmt.where(self.model.status == status)
        if category_id is not None:
            stmt = stmt.join(todo_categories).where(
                todo_categories.c.category_id == category_id
            )
        result = await db.execute(stmt)
        return result.scalar_one()

    async def search(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        query: str,
        status: str | None = None,
        category_id: int | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Todo]:
        pattern = f"%{query}%"
        stmt = (
            select(self.model)
            .options(selectinload(self.model.categories))
            .where(self.model.user_id == user_id)
            .where(
                or_(
                    self.model.title.ilike(pattern),
                    self.model.description.ilike(pattern),
                )
            )
        )
        if status is not None:
            stmt = stmt.where(self.model.status == status)
        if category_id is not None:
            stmt = stmt.join(todo_categories).where(
                todo_categories.c.category_id == category_id
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def count_search(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        query: str,
        status: str | None = None,
        category_id: int | None = None,
    ) -> int:
        pattern = f"%{query}%"
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.user_id == user_id)
            .where(
                or_(
                    self.model.title.ilike(pattern),
                    self.model.description.ilike(pattern),
                )
            )
        )
        if status is not None:
            stmt = stmt.where(self.model.status == status)
        if category_id is not None:
            stmt = stmt.join(todo_categories).where(
                todo_categories.c.category_id == category_id
            )
        result = await db.execute(stmt)
        return result.scalar_one()


todo = TodoCRUD(Todo)
