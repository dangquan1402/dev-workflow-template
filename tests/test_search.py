"""Tests for todo search feature.

Tests cover: full-text search by title/description, case-insensitivity,
status and category_id filtering, empty results, and user scoping.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.features.todo import service as todo_service
from app.features.todo.schemas import TodoListResponse


def _make_todo(
    id: int = 1,
    title: str = "Test",
    description: str | None = None,
    status: str = "pending",
    user_id: int = 1,
):
    todo = MagicMock()
    todo.id = id
    todo.title = title
    todo.description = description
    todo.status = status
    todo.user_id = user_id
    todo.categories = []
    todo.created_at = datetime(2026, 1, 1)
    todo.updated_at = datetime(2026, 1, 1)
    return todo


class TestSearchTodos:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_search_by_title(self, mock_db):
        todo = _make_todo(title="Buy groceries")
        with (
            patch(
                "app.features.todo.service.crud.todo.search",
                return_value=[todo],
            ) as mock_search,
            patch(
                "app.features.todo.service.crud.todo.count_search",
                return_value=1,
            ),
        ):
            result = await todo_service.search_todos(
                mock_db, user_id=1, query="groceries"
            )
            assert isinstance(result, TodoListResponse)
            assert result.total == 1
            assert len(result.items) == 1
            mock_search.assert_called_once_with(
                mock_db,
                user_id=1,
                query="groceries",
                status=None,
                category_id=None,
                skip=0,
                limit=20,
            )

    @pytest.mark.asyncio
    async def test_search_by_description(self, mock_db):
        todo = _make_todo(title="Task", description="milk and eggs")
        with (
            patch(
                "app.features.todo.service.crud.todo.search",
                return_value=[todo],
            ),
            patch(
                "app.features.todo.service.crud.todo.count_search",
                return_value=1,
            ),
        ):
            result = await todo_service.search_todos(mock_db, user_id=1, query="milk")
            assert result.total == 1
            assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, mock_db):
        """ILIKE handles case-insensitivity at the DB level.
        We verify the query string is passed through unchanged."""
        with (
            patch(
                "app.features.todo.service.crud.todo.search",
                return_value=[],
            ) as mock_search,
            patch(
                "app.features.todo.service.crud.todo.count_search",
                return_value=0,
            ),
        ):
            await todo_service.search_todos(mock_db, user_id=1, query="GROCERIES")
            mock_search.assert_called_once_with(
                mock_db,
                user_id=1,
                query="GROCERIES",
                status=None,
                category_id=None,
                skip=0,
                limit=20,
            )

    @pytest.mark.asyncio
    async def test_search_with_status_filter(self, mock_db):
        todo = _make_todo(title="Done task", status="done")
        with (
            patch(
                "app.features.todo.service.crud.todo.search",
                return_value=[todo],
            ) as mock_search,
            patch(
                "app.features.todo.service.crud.todo.count_search",
                return_value=1,
            ),
        ):
            result = await todo_service.search_todos(
                mock_db, user_id=1, query="task", status="done"
            )
            assert result.total == 1
            mock_search.assert_called_once_with(
                mock_db,
                user_id=1,
                query="task",
                status="done",
                category_id=None,
                skip=0,
                limit=20,
            )

    @pytest.mark.asyncio
    async def test_search_with_category_filter(self, mock_db):
        todo = _make_todo(title="Categorized task")
        with (
            patch(
                "app.features.todo.service.crud.todo.search",
                return_value=[todo],
            ) as mock_search,
            patch(
                "app.features.todo.service.crud.todo.count_search",
                return_value=1,
            ),
        ):
            result = await todo_service.search_todos(
                mock_db, user_id=1, query="task", category_id=5
            )
            assert result.total == 1
            mock_search.assert_called_once_with(
                mock_db,
                user_id=1,
                query="task",
                status=None,
                category_id=5,
                skip=0,
                limit=20,
            )

    @pytest.mark.asyncio
    async def test_search_no_matches(self, mock_db):
        with (
            patch(
                "app.features.todo.service.crud.todo.search",
                return_value=[],
            ),
            patch(
                "app.features.todo.service.crud.todo.count_search",
                return_value=0,
            ),
        ):
            result = await todo_service.search_todos(
                mock_db, user_id=1, query="nonexistent"
            )
            assert result.total == 0
            assert result.items == []

    @pytest.mark.asyncio
    async def test_search_scoped_to_user(self, mock_db):
        """Verify user_id is always passed to CRUD layer."""
        with (
            patch(
                "app.features.todo.service.crud.todo.search",
                return_value=[],
            ) as mock_search,
            patch(
                "app.features.todo.service.crud.todo.count_search",
                return_value=0,
            ) as mock_count,
        ):
            await todo_service.search_todos(mock_db, user_id=42, query="anything")
            assert mock_search.call_args[1]["user_id"] == 42
            assert mock_count.call_args[1]["user_id"] == 42
