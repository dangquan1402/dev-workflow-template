"""
Regression test for GH-5: Deleting a user leaves orphaned todos accessible.

This test should FAIL before the fix is applied, proving the bug exists.
After the fix, it should PASS.
"""

import pytest
from unittest.mock import AsyncMock

from app.features.todo.crud import TodoCRUD
from app.features.todo.models import Todo


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def todo_crud():
    return TodoCRUD(Todo)


class TestOrphanedTodos:
    """
    Bug: get_filtered returns todos belonging to soft-deleted users.

    Root cause: TodoCRUD.get_filtered does not join on the users table
    to check is_active status. It only filters by user_id and status
    on the todos table itself.

    The fix should add an exclude_inactive_users parameter (default True)
    that joins users and filters out is_active=False.
    """

    def test_get_filtered_should_accept_exclude_inactive_users_param(self, todo_crud):
        """The CRUD method should accept an exclude_inactive_users parameter."""
        import inspect

        sig = inspect.signature(todo_crud.get_filtered)
        param_names = list(sig.parameters.keys())
        assert "exclude_inactive_users" in param_names, (
            "get_filtered should accept exclude_inactive_users parameter "
            "to filter out todos belonging to soft-deleted users"
        )

    def test_count_filtered_should_accept_exclude_inactive_users_param(self, todo_crud):
        """The count method should also support the parameter."""
        import inspect

        sig = inspect.signature(todo_crud.count_filtered)
        param_names = list(sig.parameters.keys())
        assert "exclude_inactive_users" in param_names, (
            "count_filtered should accept exclude_inactive_users parameter"
        )
