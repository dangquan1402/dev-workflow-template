"""Tests for OAuth2 authentication feature.

Tests cover: provider validation, authorization URL generation,
OAuth callback flow, account linking, and account management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.security import decode_token
from app.features.oauth import service as oauth_service
from app.features.oauth.providers import (
    SUPPORTED_PROVIDERS,
    OAuthUserInfo,
    get_authorization_url,
    get_redirect_uri,
)


# --- Provider tests ---


class TestProviderConfig:
    def test_supported_providers(self):
        assert "google" in SUPPORTED_PROVIDERS
        assert "github" in SUPPORTED_PROVIDERS

    def test_redirect_uri_format(self):
        uri = get_redirect_uri("google")
        assert "/api/v1/auth/oauth/google/callback" in uri

    def test_authorization_url_google(self):
        url = get_authorization_url("google", state="test-state")
        assert "accounts.google.com" in url
        assert "test-state" in url

    def test_authorization_url_github(self):
        url = get_authorization_url("github", state="test-state")
        assert "github.com/login/oauth/authorize" in url
        assert "test-state" in url


# --- Service tests ---


class TestGetOrCreateUserFromOAuth:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.fixture
    def google_user_info(self):
        return OAuthUserInfo(
            provider="google",
            provider_user_id="12345",
            email="test@gmail.com",
            name="Test User",
        )

    @pytest.mark.asyncio
    async def test_existing_oauth_link_returns_tokens(self, mock_db, google_user_info):
        """If OAuth account already linked, return tokens for that user."""
        existing_link = MagicMock()
        existing_link.user_id = 42

        with patch(
            "app.features.oauth.service.crud.oauth_account.get_by_provider",
            return_value=existing_link,
        ):
            tokens, is_new = await oauth_service.get_or_create_user_from_oauth(
                mock_db, google_user_info
            )
            assert "access_token" in tokens
            assert "refresh_token" in tokens
            assert is_new is False
            # Verify token contains the right user ID
            user_id = decode_token(tokens["access_token"], expected_type="access")
            assert user_id == 42

    @pytest.mark.asyncio
    async def test_existing_email_links_oauth_account(self, mock_db, google_user_info):
        """If user with same email exists, link OAuth account to them."""
        existing_user = MagicMock()
        existing_user.id = 10

        with (
            patch(
                "app.features.oauth.service.crud.oauth_account.get_by_provider",
                return_value=None,
            ),
            patch(
                "app.features.oauth.service.user_service.get_by_email",
                return_value=existing_user,
            ),
            patch(
                "app.features.oauth.service.crud.oauth_account.create",
                return_value=MagicMock(),
            ) as mock_create,
        ):
            tokens, is_new = await oauth_service.get_or_create_user_from_oauth(
                mock_db, google_user_info
            )
            assert is_new is False
            assert decode_token(tokens["access_token"], expected_type="access") == 10
            # Verify OAuth account was created with correct data
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]["obj_in"]
            assert call_kwargs["user_id"] == 10
            assert call_kwargs["provider"] == "google"
            assert call_kwargs["provider_user_id"] == "12345"

    @pytest.mark.asyncio
    async def test_new_user_created_from_oauth(self, mock_db, google_user_info):
        """If no matching user, create new user and link OAuth account."""
        new_user = MagicMock()
        new_user.id = 99

        with (
            patch(
                "app.features.oauth.service.crud.oauth_account.get_by_provider",
                return_value=None,
            ),
            patch(
                "app.features.oauth.service.user_service.get_by_email",
                return_value=None,
            ),
            patch(
                "app.features.oauth.service.user_service.create_user",
                return_value=new_user,
            ) as mock_create_user,
            patch(
                "app.features.oauth.service.crud.oauth_account.create",
                return_value=MagicMock(),
            ),
        ):
            tokens, is_new = await oauth_service.get_or_create_user_from_oauth(
                mock_db, google_user_info
            )
            assert is_new is True
            assert decode_token(tokens["access_token"], expected_type="access") == 99
            mock_create_user.assert_called_once()


class TestListUserOAuthAccounts:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_returns_accounts(self, mock_db):
        accounts = [MagicMock(), MagicMock()]
        with patch(
            "app.features.oauth.service.crud.oauth_account.get_by_user",
            return_value=accounts,
        ):
            result = await oauth_service.list_user_oauth_accounts(mock_db, user_id=1)
            assert len(result) == 2


class TestUnlinkOAuthAccount:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_unlink_not_found(self, mock_db):
        with patch(
            "app.features.oauth.service.crud.oauth_account.get",
            return_value=None,
        ):
            result = await oauth_service.unlink_oauth_account(
                mock_db, account_id=1, user_id=1
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_unlink_wrong_user(self, mock_db):
        account = MagicMock()
        account.user_id = 99  # different user

        with patch(
            "app.features.oauth.service.crud.oauth_account.get",
            return_value=account,
        ):
            result = await oauth_service.unlink_oauth_account(
                mock_db, account_id=1, user_id=1
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_unlink_last_method_raises(self, mock_db):
        account = MagicMock()
        account.user_id = 1

        user = MagicMock()
        user.hashed_password = None  # no password set

        with (
            patch(
                "app.features.oauth.service.crud.oauth_account.get",
                return_value=account,
            ),
            patch(
                "app.features.oauth.service.user_service.get_user",
                return_value=user,
            ),
            patch(
                "app.features.oauth.service.crud.oauth_account.count_by_user",
                return_value=1,
            ),
        ):
            with pytest.raises(ValueError, match="Cannot unlink last login method"):
                await oauth_service.unlink_oauth_account(
                    mock_db, account_id=1, user_id=1
                )

    @pytest.mark.asyncio
    async def test_unlink_success_with_password(self, mock_db):
        account = MagicMock()
        account.user_id = 1

        user = MagicMock()
        user.hashed_password = "some-hash"

        with (
            patch(
                "app.features.oauth.service.crud.oauth_account.get",
                return_value=account,
            ),
            patch(
                "app.features.oauth.service.user_service.get_user",
                return_value=user,
            ),
            patch(
                "app.features.oauth.service.crud.oauth_account.count_by_user",
                return_value=1,
            ),
            patch(
                "app.features.oauth.service.crud.oauth_account.delete",
                return_value=account,
            ),
        ):
            result = await oauth_service.unlink_oauth_account(
                mock_db, account_id=1, user_id=1
            )
            assert result is account

    @pytest.mark.asyncio
    async def test_unlink_success_with_multiple_oauth(self, mock_db):
        account = MagicMock()
        account.user_id = 1

        user = MagicMock()
        user.hashed_password = None  # no password

        with (
            patch(
                "app.features.oauth.service.crud.oauth_account.get",
                return_value=account,
            ),
            patch(
                "app.features.oauth.service.user_service.get_user",
                return_value=user,
            ),
            patch(
                "app.features.oauth.service.crud.oauth_account.count_by_user",
                return_value=2,  # another OAuth link exists
            ),
            patch(
                "app.features.oauth.service.crud.oauth_account.delete",
                return_value=account,
            ),
        ):
            result = await oauth_service.unlink_oauth_account(
                mock_db, account_id=1, user_id=1
            )
            assert result is account
