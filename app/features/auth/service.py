import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.features.user import service as user_service
from app.features.user.models import User
from app.features.user.schemas import UserCreate


async def register(db: AsyncSession, email: str, password: str, name: str) -> User:
    return await user_service.create_user(
        db, user_in=UserCreate(email=email, password=password, name=name)
    )


async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
    user = await user_service.get_by_email(db, email=email)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_tokens(user_id: uuid.UUID) -> dict[str, str]:
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
    }


def refresh_access_token(refresh_token: str) -> str | None:
    user_id = decode_token(refresh_token, expected_type="refresh")
    if user_id is None:
        return None
    return create_access_token(user_id)
