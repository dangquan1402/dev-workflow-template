import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# --- Request schemas ---


class CategoryCreate(BaseModel):
    """POST /api/v1/categories"""

    name: str
    color: str | None = None
    user_id: uuid.UUID | None = None  # Set by router from token


class CategoryUpdate(BaseModel):
    """PATCH /api/v1/categories/{id}"""

    name: str | None = None
    color: str | None = None


# --- Response schemas ---


class CategoryResponse(BaseModel):
    """Single category response."""

    id: uuid.UUID
    name: str
    color: str | None
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    """Paginated category list."""

    items: list[CategoryResponse]
    total: int
