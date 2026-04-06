from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.rate_limit import rate_limit
from app.core.config import settings
from app.features.user.models import User
from app.features.user.schemas import UserResponse

from . import schemas, service
from .dependencies import get_current_user

router = APIRouter()

_auth_rate_limit = rate_limit(
    max_requests=settings.RATE_LIMIT_AUTH_PER_MINUTE, window_seconds=60
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_auth_rate_limit)],
)
async def register(body: schemas.RegisterRequest, db: AsyncSession = Depends(get_db)):
    from app.features.user import service as user_service

    existing = await user_service.get_by_email(db, email=body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return await service.register(
        db, email=body.email, password=body.password, name=body.name
    )


@router.post(
    "/login",
    response_model=schemas.TokenResponse,
    dependencies=[Depends(_auth_rate_limit)],
)
async def login(body: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await service.authenticate(db, email=body.email, password=body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return service.create_tokens(user.id)


@router.post(
    "/refresh",
    response_model=schemas.RefreshResponse,
    dependencies=[Depends(_auth_rate_limit)],
)
async def refresh(body: schemas.RefreshRequest):
    access_token = service.refresh_access_token(body.refresh_token)
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
