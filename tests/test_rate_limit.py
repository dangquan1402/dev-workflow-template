"""Tests for Redis-backed rate limiting dependency.

Tests cover: key generation, rate limit enforcement, 429 response,
and authenticated vs unauthenticated identifier selection.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException

from app.common.rate_limit import _get_identifier, rate_limit


class TestGetIdentifier:
    """Test identifier extraction from request objects."""

    def _make_request(self, *, user_id=None, client_host="127.0.0.1"):
        request = MagicMock()
        request.state = MagicMock()
        if user_id is not None:
            request.state.user_id = user_id
        else:
            # Simulate missing attribute
            del request.state.user_id
        request.client = MagicMock()
        request.client.host = client_host
        return request

    def test_authenticated_user_returns_user_id(self):
        request = self._make_request(user_id=42)
        assert _get_identifier(request) == "user:42"

    def test_unauthenticated_returns_ip(self):
        request = self._make_request(client_host="10.0.0.1")
        assert _get_identifier(request) == "ip:10.0.0.1"

    def test_no_client_returns_unknown(self):
        request = MagicMock()
        request.state = MagicMock()
        del request.state.user_id
        request.client = None
        assert _get_identifier(request) == "ip:unknown"


class TestRateLimitDependency:
    """Test the rate_limit dependency factory."""

    @pytest.fixture
    def mock_redis(self):
        redis = AsyncMock()
        redis.incr = AsyncMock(return_value=1)
        redis.expire = AsyncMock()
        redis.ttl = AsyncMock(return_value=45)
        return redis

    @pytest.fixture
    def mock_request(self):
        request = MagicMock()
        request.state = MagicMock()
        del request.state.user_id
        request.client = MagicMock()
        request.client.host = "192.168.1.1"
        request.scope = {"path": "/api/v1/auth/login"}
        return request

    @pytest.mark.asyncio
    async def test_allows_request_under_limit(self, mock_redis, mock_request):
        dep = rate_limit(max_requests=10, window_seconds=60)
        mock_redis.incr.return_value = 5
        # Should not raise
        await dep(request=mock_request, redis=mock_redis)
        mock_redis.incr.assert_called_once()

    @pytest.mark.asyncio
    async def test_sets_expire_on_first_request(self, mock_redis, mock_request):
        dep = rate_limit(max_requests=10, window_seconds=60)
        mock_redis.incr.return_value = 1
        await dep(request=mock_request, redis=mock_redis)
        mock_redis.expire.assert_called_once()
        # Verify the TTL passed to expire
        args = mock_redis.expire.call_args
        assert args[0][1] == 60

    @pytest.mark.asyncio
    async def test_does_not_set_expire_on_subsequent_requests(
        self, mock_redis, mock_request
    ):
        dep = rate_limit(max_requests=10, window_seconds=60)
        mock_redis.incr.return_value = 5
        await dep(request=mock_request, redis=mock_redis)
        mock_redis.expire.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_429_when_limit_exceeded(self, mock_redis, mock_request):
        dep = rate_limit(max_requests=10, window_seconds=60)
        mock_redis.incr.return_value = 11
        mock_redis.ttl.return_value = 30

        with pytest.raises(HTTPException) as exc_info:
            await dep(request=mock_request, redis=mock_redis)

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail
        assert exc_info.value.headers["Retry-After"] == "30"

    @pytest.mark.asyncio
    async def test_retry_after_minimum_is_one(self, mock_redis, mock_request):
        dep = rate_limit(max_requests=5, window_seconds=60)
        mock_redis.incr.return_value = 6
        mock_redis.ttl.return_value = -1  # Key has no TTL (edge case)

        with pytest.raises(HTTPException) as exc_info:
            await dep(request=mock_request, redis=mock_redis)

        assert exc_info.value.headers["Retry-After"] == "1"

    @pytest.mark.asyncio
    async def test_key_includes_identifier_and_path(self, mock_redis, mock_request):
        dep = rate_limit(max_requests=10, window_seconds=60)
        mock_redis.incr.return_value = 1
        await dep(request=mock_request, redis=mock_redis)

        key = mock_redis.incr.call_args[0][0]
        assert key == "rate_limit:ip:192.168.1.1:/api/v1/auth/login"

    @pytest.mark.asyncio
    async def test_authenticated_user_key(self, mock_redis):
        request = MagicMock()
        request.state = MagicMock()
        request.state.user_id = 99
        request.client = MagicMock()
        request.client.host = "10.0.0.1"
        request.scope = {"path": "/api/v1/todos/"}

        dep = rate_limit(max_requests=60, window_seconds=60)
        mock_redis.incr.return_value = 1
        await dep(request=request, redis=mock_redis)

        key = mock_redis.incr.call_args[0][0]
        assert key == "rate_limit:user:99:/api/v1/todos/"

    @pytest.mark.asyncio
    async def test_exactly_at_limit_is_allowed(self, mock_redis, mock_request):
        dep = rate_limit(max_requests=10, window_seconds=60)
        mock_redis.incr.return_value = 10  # Exactly at limit, not over
        # Should not raise
        await dep(request=mock_request, redis=mock_redis)
