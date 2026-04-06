from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud import GenericCRUD
from app.features.user.models import User

from .models import Todo


class TodoCRUD(GenericCRUD[Todo]):
    async def get_by_user(
        self, db: AsyncSession, user_id: int, *, skip: int = 0, limit: int = 20
    ) -> list[Todo]:
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
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
        exclude_inactive_users: bool = True,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Todo]:
        stmt = select(self.model)
        if exclude_inactive_users:
            stmt = stmt.join(User, self.model.user_id == User.id).where(
                User.is_active.is_(True)
            )
        if user_id is not None:
            stmt = stmt.where(self.model.user_id == user_id)
        if status is not None:
            stmt = stmt.where(self.model.status == status)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        db: AsyncSession,
        *,
        user_id: int | None = None,
        status: str | None = None,
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
        result = await db.execute(stmt)
        return result.scalar_one()


todo = TodoCRUD(Todo)
