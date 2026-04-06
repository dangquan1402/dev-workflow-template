from pydantic import BaseModel, EmailStr


# --- Request schemas ---


class RegisterRequest(BaseModel):
    """POST /api/v1/auth/register"""

    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    """POST /api/v1/auth/login"""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """POST /api/v1/auth/refresh"""

    refresh_token: str


# --- Response schemas ---


class TokenResponse(BaseModel):
    """POST /api/v1/auth/login response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshResponse(BaseModel):
    """POST /api/v1/auth/refresh response"""

    access_token: str
    token_type: str = "bearer"
