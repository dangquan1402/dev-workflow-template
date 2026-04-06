from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.features.category.schemas import CategoryResponse


class TodoStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


# --- Request schemas ---


class TodoCreate(BaseModel):
    """POST /api/v1/todos"""

    title: str
    description: str | None = None
    user_id: int
    category_ids: list[int] = []


class TodoUpdate(BaseModel):
    """PATCH /api/v1/todos/{id}"""

    title: str | None = None
    description: str | None = None
    status: TodoStatus | None = None
    category_ids: list[int] | None = None


# --- Response schemas ---


class TodoResponse(BaseModel):
    """Single todo response."""

    id: int
    title: str
    description: str | None
    status: TodoStatus
    user_id: int
    categories: list[CategoryResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TodoListResponse(BaseModel):
    """Paginated todo list."""

    items: list[TodoResponse]
    total: int
