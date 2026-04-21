"""OAuth2 business logic: link accounts, create users, generate tokens."""

import secrets
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.service import create_tokens
from app.features.user import service as user_service
from app.features.user.schemas import UserCreate

from . import crud
from .models import OAuthAccount
from .providers import OAuthUserInfo


async def get_or_create_user_from_oauth(
    db: AsyncSession, user_info: OAuthUserInfo
) -> tuple[dict[str, str], bool]:
    """Handle OAuth2 callback: find/create user, link account, return tokens.

    Returns (token_dict, is_new_user).
    """
    # Check if this OAuth account is already linked
    existing_link = await crud.oauth_account.get_by_provider(
        db, provider=user_info.provider, provider_user_id=user_info.provider_user_id
    )
    if existing_link:
        tokens = create_tokens(existing_link.user_id)
        return tokens, False

    # Check if a user with this email already exists
    existing_user = await user_service.get_by_email(db, email=user_info.email)
    is_new_user = existing_user is None

    if is_new_user:
        # Create a new user with a random password (they'll use OAuth to log in)
        random_password = secrets.token_urlsafe(32)
        user = await user_service.create_user(
            db,
            user_in=UserCreate(
                email=user_info.email,
                password=random_password,
                name=user_info.name,
            ),
        )
    else:
        user = existing_user

    # Link the OAuth account
    await crud.oauth_account.create(
        db,
        obj_in={
            "user_id": user.id,
            "provider": user_info.provider,
            "provider_user_id": user_info.provider_user_id,
            "provider_email": user_info.email,
        },
    )

    tokens = create_tokens(user.id)
    return tokens, is_new_user


async def list_user_oauth_accounts(
    db: AsyncSession, user_id: uuid.UUID
) -> list[OAuthAccount]:
    return await crud.oauth_account.get_by_user(db, user_id=user_id)


async def unlink_oauth_account(
    db: AsyncSession, account_id: uuid.UUID, user_id: uuid.UUID
) -> OAuthAccount | None:
    """Unlink an OAuth account. Returns None if not found/not owned."""
    account = await crud.oauth_account.get(db, account_id)
    if account is None or account.user_id != user_id:
        return None

    # Check if user has a password set (non-random) or other OAuth links
    user = await user_service.get_user(db, user_id=user_id)
    oauth_count = await crud.oauth_account.count_by_user(db, user_id=user_id)

    # If no password and this is the last OAuth link, deny
    has_password = user is not None and user.hashed_password is not None
    if oauth_count <= 1 and not has_password:
        raise ValueError("Cannot unlink last login method")

    await crud.oauth_account.delete(db, id=account_id)
    return account
