from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud import GenericCRUD

from .models import User


class UserCRUD(GenericCRUD[User]):
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalar_one_or_none()


user = UserCRUD(User)
