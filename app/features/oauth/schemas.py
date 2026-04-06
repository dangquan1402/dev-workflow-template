from datetime import datetime

from pydantic import BaseModel, ConfigDict


# --- Response schemas ---


class OAuthAuthorizeResponse(BaseModel):
    """GET /api/v1/auth/oauth/{provider}/authorize response"""

    authorization_url: str


class OAuthCallbackResponse(BaseModel):
    """GET /api/v1/auth/oauth/{provider}/callback response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool


class OAuthProvidersResponse(BaseModel):
    """GET /api/v1/auth/oauth/providers response"""

    providers: list[str]


class OAuthAccountResponse(BaseModel):
    """Single OAuth account linked to a user."""

    id: int
    provider: str
    provider_email: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OAuthAccountsListResponse(BaseModel):
    """GET /api/v1/auth/oauth/accounts response"""

    accounts: list[OAuthAccountResponse]
