from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud import GenericCRUD

from .models import Todo


class TodoCRUD(GenericCRUD[Todo]):
    async def get_by_user(
        self, db: AsyncSession, user_id: int, *, skip: int = 0, limit: int = 20
    ) -> list[Todo]:
        stmt = select(self.model).where(self.model.user_id == user_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(
        self, db: AsyncSession, status: str, *, skip: int = 0, limit: int = 20
    ) -> list[Todo]:
        stmt = select(self.model).where(self.model.status == status).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_filtered(
        self,
        db: AsyncSession,
        *,
        user_id: int | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Todo]:
        stmt = select(self.model)
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
    ) -> int:
        stmt = select(func.count()).select_from(self.model)
        if user_id is not None:
            stmt = stmt.where(self.model.user_id == user_id)
        if status is not None:
            stmt = stmt.where(self.model.status == status)
        result = await db.execute(stmt)
        return result.scalar_one()


todo = TodoCRUD(Todo)
