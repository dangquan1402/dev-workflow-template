from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud import GenericCRUD

from .models import Category


class CategoryCRUD(GenericCRUD[Category]):
    async def get_by_user(
        self, db: AsyncSession, user_id: int, *, skip: int = 0, limit: int = 20
    ) -> list[Category]:
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(self, db: AsyncSession, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.user_id == user_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one()


category = CategoryCRUD(Category)
