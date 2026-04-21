import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud import GenericCRUD

from .models import OAuthAccount


class OAuthAccountCRUD(GenericCRUD[OAuthAccount]):
    async def get_by_provider(
        self,
        db: AsyncSession,
        *,
        provider: str,
        provider_user_id: str,
    ) -> OAuthAccount | None:
        result = await db.execute(
            select(self.model).where(
                self.model.provider == provider,
                self.model.provider_user_id == provider_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self, db: AsyncSession, *, user_id: uuid.UUID
    ) -> list[OAuthAccount]:
        result = await db.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return list(result.scalars().all())

    async def count_by_user(self, db: AsyncSession, *, user_id: uuid.UUID) -> int:
        result = await db.execute(
            select(func.count())
            .select_from(self.model)
            .where(self.model.user_id == user_id)
        )
        return result.scalar_one()


oauth_account = OAuthAccountCRUD(OAuthAccount)
