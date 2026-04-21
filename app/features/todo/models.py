import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.database import Base
from app.common.models import TimestampMixin, UUIDMixin
from app.features.category.models import todo_categories


class Todo(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "todos"

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="pending", index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    user = relationship("User", backref="todos")
    categories = relationship(
        "Category", secondary=todo_categories, back_populates="todos"
    )
