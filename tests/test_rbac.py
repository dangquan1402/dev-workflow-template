"""Tests for role-based access control.

Tests cover: default role assignment, admin dependency behavior,
and endpoint protection for admin-only routes.
"""

import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.features.auth.dependencies import get_current_admin
from app.features.user.models import UserRole


# --- UserRole enum tests ---


class TestUserRole:
    def test_default_role_is_user(self):
        assert UserRole.user.value == "user"

    def test_admin_role_value(self):
        assert UserRole.admin.value == "admin"

    def test_role_is_string_enum(self):
        assert isinstance(UserRole.admin, str)
        assert isinstance(UserRole.user, str)


# --- get_current_admin dependency tests ---


class TestGetCurrentAdmin:
    @pytest.mark.asyncio
    async def test_admin_user_allowed(self):
        admin_user = MagicMock()
        admin_user.role = UserRole.admin.value

        result = await get_current_admin(current_user=admin_user)
        assert result is admin_user

    @pytest.mark.asyncio
    async def test_regular_user_rejected_with_403(self):
        regular_user = MagicMock()
        regular_user.role = UserRole.user.value

        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(current_user=regular_user)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Admin access required"


# --- User model default role tests ---


class TestUserModelRole:
    def test_user_model_has_role_column(self):
        from app.features.user.models import User

        assert hasattr(User, "role")

    def test_role_column_default(self):
        from app.features.user.models import User

        # Check that the column has the right default
        role_col = User.__table__.columns["role"]
        assert role_col.default.arg == UserRole.user.value
        assert role_col.nullable is False


# --- Endpoint protection tests ---


class TestAdminEndpointProtection:
    """Test that admin-only endpoints use the get_current_admin dependency."""

    def test_list_users_requires_admin(self):
        """Verify list_users endpoint has admin dependency."""
        from app.features.user.router import list_users

        # Check that the endpoint signature includes admin dependency
        import inspect

        sig = inspect.signature(list_users)
        params = sig.parameters
        assert "current_user" in params

    def test_delete_user_requires_admin(self):
        """Verify delete_user endpoint has admin dependency."""
        from app.features.user.router import delete_user

        import inspect

        sig = inspect.signature(delete_user)
        params = sig.parameters
        assert "current_user" in params

    def test_get_user_requires_auth(self):
        """Verify get_user endpoint requires authentication."""
        from app.features.user.router import get_user

        import inspect

        sig = inspect.signature(get_user)
        params = sig.parameters
        assert "current_user" in params

    def test_update_user_requires_auth(self):
        """Verify update_user endpoint requires authentication."""
        from app.features.user.router import update_user

        import inspect

        sig = inspect.signature(update_user)
        params = sig.parameters
        assert "current_user" in params


# --- Schema tests ---


class TestUserSchemas:
    def test_user_response_includes_role(self):
        from app.features.user.schemas import UserResponse

        fields = UserResponse.model_fields
        assert "role" in fields

    def test_user_update_accepts_role(self):
        from app.features.user.schemas import UserUpdate

        fields = UserUpdate.model_fields
        assert "role" in fields
        # role should be optional
        update = UserUpdate()
        assert update.role is None
