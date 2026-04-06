import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.rate_limit import rate_limit
from app.core.config import settings
from app.features.auth.dependencies import get_current_user
from app.features.user.models import User

from . import schemas, service
from .providers import (
    SUPPORTED_PROVIDERS,
    exchange_code_for_user_info,
    get_authorization_url,
)

router = APIRouter()

_oauth_rate_limit = rate_limit(
    max_requests=settings.RATE_LIMIT_AUTH_PER_MINUTE, window_seconds=60
)


def _validate_provider(provider: str) -> None:
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}. Supported: {SUPPORTED_PROVIDERS}",
        )


@router.get(
    "/{provider}/authorize",
    response_model=schemas.OAuthAuthorizeResponse,
    dependencies=[Depends(_oauth_rate_limit)],
)
async def authorize(provider: str):
    _validate_provider(provider)
    state = secrets.token_urlsafe(32)
    url = get_authorization_url(provider, state=state)
    return {"authorization_url": url}


@router.get(
    "/{provider}/callback",
    response_model=schemas.OAuthCallbackResponse,
    dependencies=[Depends(_oauth_rate_limit)],
)
async def callback(
    provider: str,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    _validate_provider(provider)

    try:
        user_info = await exchange_code_for_user_info(provider, code)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate with provider",
        )

    try:
        tokens, is_new_user = await service.get_or_create_user_from_oauth(db, user_info)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Provider email already linked to a different account",
        )

    return {**tokens, "is_new_user": is_new_user}


@router.get("/providers", response_model=schemas.OAuthProvidersResponse)
async def list_providers():
    return {"providers": SUPPORTED_PROVIDERS}


@router.get("/accounts", response_model=schemas.OAuthAccountsListResponse)
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    accounts = await service.list_user_oauth_accounts(db, user_id=current_user.id)
    return {"accounts": accounts}


@router.delete(
    "/accounts/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unlink_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await service.unlink_oauth_account(
            db, account_id=account_id, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth account not found",
        )
