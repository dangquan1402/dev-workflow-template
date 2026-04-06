from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud import GenericCRUD
from .models import Comment


class CommentCRUD(GenericCRUD[Comment]):
    async def get_by_todo(
        self, db: AsyncSession, todo_id: int, skip: int = 0, limit: int = 20
    ) -> list[Comment]:
        result = await db.execute(
            select(Comment)
            .where(Comment.todo_id == todo_id)
            .order_by(Comment.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_todo(self, db: AsyncSession, todo_id: int) -> int:
        result = await db.execute(
            select(func.count()).select_from(Comment).where(Comment.todo_id == todo_id)
        )
        return result.scalar_one()


comment = CommentCRUD(Comment)
