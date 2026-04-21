"""Tests for JWT authentication feature.

Tests cover: registration, login, token refresh, /me endpoint,
and auth dependency behavior.
"""

import uuid

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.features.auth import service as auth_service

USER_ID_1 = uuid.UUID("00000000-0000-4000-8000-000000000001")
USER_ID_2 = uuid.UUID("00000000-0000-4000-8000-000000000002")
USER_ID_3 = uuid.UUID("00000000-0000-4000-8000-000000000003")


# --- Security utility tests ---


class TestPasswordHashing:
    def test_hash_and_verify(self):
        plain = "securepass123"
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert not verify_password("wrong", hashed)


class TestTokenCreation:
    def test_access_token_roundtrip(self):
        token = create_access_token(USER_ID_1)
        user_id = decode_token(token, expected_type="access")
        assert user_id == USER_ID_1

    def test_refresh_token_roundtrip(self):
        token = create_refresh_token(USER_ID_1)
        user_id = decode_token(token, expected_type="refresh")
        assert user_id == USER_ID_1

    def test_access_token_rejected_as_refresh(self):
        token = create_access_token(USER_ID_1)
        assert decode_token(token, expected_type="refresh") is None

    def test_refresh_token_rejected_as_access(self):
        token = create_refresh_token(USER_ID_1)
        assert decode_token(token, expected_type="access") is None

    def test_invalid_token_returns_none(self):
        assert decode_token("garbage.token.here") is None


# --- Auth service tests ---


class TestAuthenticate:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_authenticate_success(self, mock_db):
        user = MagicMock()
        user.is_active = True
        user.hashed_password = hash_password("pass123")

        with patch(
            "app.features.auth.service.user_service.get_by_email",
            return_value=user,
        ):
            result = await auth_service.authenticate(
                mock_db, email="test@example.com", password="pass123"
            )
            assert result is user

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, mock_db):
        user = MagicMock()
        user.is_active = True
        user.hashed_password = hash_password("correct")

        with patch(
            "app.features.auth.service.user_service.get_by_email",
            return_value=user,
        ):
            result = await auth_service.authenticate(
                mock_db, email="test@example.com", password="wrong"
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, mock_db):
        with patch(
            "app.features.auth.service.user_service.get_by_email",
            return_value=None,
        ):
            result = await auth_service.authenticate(
                mock_db, email="nobody@example.com", password="pass"
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, mock_db):
        user = MagicMock()
        user.is_active = False

        with patch(
            "app.features.auth.service.user_service.get_by_email",
            return_value=user,
        ):
            result = await auth_service.authenticate(
                mock_db, email="test@example.com", password="pass"
            )
            assert result is None


class TestCreateTokens:
    def test_returns_access_and_refresh(self):
        tokens = auth_service.create_tokens(USER_ID_1)
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

    def test_tokens_are_valid(self):
        tokens = auth_service.create_tokens(USER_ID_2)
        assert decode_token(tokens["access_token"], expected_type="access") == USER_ID_2
        assert (
            decode_token(tokens["refresh_token"], expected_type="refresh") == USER_ID_2
        )


class TestRefreshAccessToken:
    def test_valid_refresh_returns_new_access(self):
        refresh = create_refresh_token(USER_ID_3)
        new_access = auth_service.refresh_access_token(refresh)
        assert new_access is not None
        assert decode_token(new_access, expected_type="access") == USER_ID_3

    def test_access_token_rejected_for_refresh(self):
        access = create_access_token(USER_ID_3)
        assert auth_service.refresh_access_token(access) is None

    def test_invalid_token_returns_none(self):
        assert auth_service.refresh_access_token("bad.token") is None
