from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


# --- Request schemas (what the client sends) ---


class UserCreate(BaseModel):
    """POST /api/v1/users"""

    email: EmailStr
    password: str
    name: str


class UserUpdate(BaseModel):
    """PATCH /api/v1/users/{id}"""

    name: str | None = None
    email: EmailStr | None = None
    role: str | None = None


# --- Response schemas (what the API returns) ---


class UserResponse(BaseModel):
    """Single user response. Never includes password."""

    id: int
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Paginated user list."""

    items: list[UserResponse]
    total: int
