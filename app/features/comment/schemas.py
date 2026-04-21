from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class CommentCreate(BaseModel):
    """POST request body"""

    body: str

    @field_validator("body")
    @classmethod
    def body_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Comment body must not be empty")
        return v


class CommentUpdate(BaseModel):
    """PATCH request body — all optional"""

    body: str | None = None

    @field_validator("body")
    @classmethod
    def body_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Comment body must not be empty")
        return v


class CommentResponse(BaseModel):
    id: int
    body: str
    todo_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    total: int
