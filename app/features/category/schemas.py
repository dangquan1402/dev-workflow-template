from datetime import datetime

from pydantic import BaseModel, ConfigDict


# --- Request schemas ---


class CategoryCreate(BaseModel):
    """POST /api/v1/categories"""

    name: str
    color: str | None = None
    user_id: int = 0  # Set by router from token


class CategoryUpdate(BaseModel):
    """PATCH /api/v1/categories/{id}"""

    name: str | None = None
    color: str | None = None


# --- Response schemas ---


class CategoryResponse(BaseModel):
    """Single category response."""

    id: int
    name: str
    color: str | None
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    """Paginated category list."""

    items: list[CategoryResponse]
    total: int
