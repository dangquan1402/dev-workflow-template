"""Tests for WebSocket todo notifications.

Tests cover: ConnectionManager, notify_todo_event, and WS router auth.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.features.ws.manager import ConnectionManager
from app.features.ws.events import notify_todo_event


# --- ConnectionManager tests ---


class TestConnectionManager:
    @pytest.fixture
    def mgr(self):
        return ConnectionManager()

    @pytest.fixture
    def mock_ws(self):
        ws = AsyncMock()
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_connect_accepts_and_stores(self, mgr, mock_ws):
        await mgr.connect(mock_ws, user_id=1)
        mock_ws.accept.assert_awaited_once()
        assert 1 in mgr.active_connections
        assert mock_ws in mgr.active_connections[1]

    @pytest.mark.asyncio
    async def test_connect_multiple_for_same_user(self, mgr):
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await mgr.connect(ws1, user_id=1)
        await mgr.connect(ws2, user_id=1)
        assert len(mgr.active_connections[1]) == 2

    @pytest.mark.asyncio
    async def test_disconnect_removes_connection(self, mgr, mock_ws):
        await mgr.connect(mock_ws, user_id=1)
        mgr.disconnect(mock_ws, user_id=1)
        assert 1 not in mgr.active_connections

    @pytest.mark.asyncio
    async def test_disconnect_keeps_other_connections(self, mgr):
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await mgr.connect(ws1, user_id=1)
        await mgr.connect(ws2, user_id=1)
        mgr.disconnect(ws1, user_id=1)
        assert len(mgr.active_connections[1]) == 1
        assert ws2 in mgr.active_connections[1]

    @pytest.mark.asyncio
    async def test_send_to_user(self, mgr, mock_ws):
        await mgr.connect(mock_ws, user_id=1)
        msg = {"event": "todo.created", "data": {"id": 1}}
        await mgr.send_to_user(1, msg)
        mock_ws.send_json.assert_awaited_once_with(msg)

    @pytest.mark.asyncio
    async def test_send_to_user_no_connections(self, mgr):
        # Should not raise
        await mgr.send_to_user(999, {"event": "test"})

    @pytest.mark.asyncio
    async def test_send_to_user_handles_broken_connection(self, mgr):
        ws = AsyncMock()
        ws.send_json = AsyncMock(side_effect=RuntimeError("closed"))
        await mgr.connect(ws, user_id=1)
        # Should not raise despite the error
        await mgr.send_to_user(1, {"event": "test"})

    @pytest.mark.asyncio
    async def test_broadcast(self, mgr):
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await mgr.connect(ws1, user_id=1)
        await mgr.connect(ws2, user_id=2)
        msg = {"event": "todo.created", "data": {}}
        await mgr.broadcast(msg)
        ws1.send_json.assert_awaited_once_with(msg)
        ws2.send_json.assert_awaited_once_with(msg)

    @pytest.mark.asyncio
    async def test_broadcast_with_exclude(self, mgr):
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await mgr.connect(ws1, user_id=1)
        await mgr.connect(ws2, user_id=2)
        msg = {"event": "todo.created", "data": {}}
        await mgr.broadcast(msg, exclude_user_id=1)
        ws1.send_json.assert_not_awaited()
        ws2.send_json.assert_awaited_once_with(msg)


# --- Event helper tests ---


class TestNotifyTodoEvent:
    @pytest.mark.asyncio
    async def test_notify_sends_correct_message(self):
        with patch(
            "app.features.ws.events.manager.send_to_user", new_callable=AsyncMock
        ) as mock_send:
            todo_data = {"id": 1, "title": "Test"}
            await notify_todo_event(
                user_id=42, event_type="todo.created", todo_data=todo_data
            )
            mock_send.assert_awaited_once_with(
                42,
                {"event": "todo.created", "data": {"id": 1, "title": "Test"}},
            )


# --- WebSocket router auth tests ---


class TestWebSocketAuth:
    @pytest.mark.asyncio
    async def test_invalid_token_closes_with_4001(self):
        from app.features.ws.router import todo_websocket

        mock_ws = AsyncMock()
        mock_db = AsyncMock()

        with patch("app.features.ws.router.decode_token", return_value=None):
            await todo_websocket(
                websocket=mock_ws,
                token="bad.token",
                subscribe_all=False,
                db=mock_db,
            )
            mock_ws.close.assert_awaited_once_with(code=4001, reason="Invalid token")

    @pytest.mark.asyncio
    async def test_inactive_user_closes_with_4001(self):
        from app.features.ws.router import todo_websocket

        mock_ws = AsyncMock()
        mock_db = AsyncMock()
        user = MagicMock()
        user.is_active = False

        with (
            patch("app.features.ws.router.decode_token", return_value=1),
            patch(
                "app.features.ws.router.user_service.get_user",
                return_value=user,
            ),
        ):
            await todo_websocket(
                websocket=mock_ws,
                token="valid.token",
                subscribe_all=False,
                db=mock_db,
            )
            mock_ws.close.assert_awaited_once_with(code=4001, reason="Invalid user")

    @pytest.mark.asyncio
    async def test_user_not_found_closes_with_4001(self):
        from app.features.ws.router import todo_websocket

        mock_ws = AsyncMock()
        mock_db = AsyncMock()

        with (
            patch("app.features.ws.router.decode_token", return_value=1),
            patch(
                "app.features.ws.router.user_service.get_user",
                return_value=None,
            ),
        ):
            await todo_websocket(
                websocket=mock_ws,
                token="valid.token",
                subscribe_all=False,
                db=mock_db,
            )
            mock_ws.close.assert_awaited_once_with(code=4001, reason="Invalid user")

    @pytest.mark.asyncio
    async def test_valid_user_connects_and_disconnect_cleanup(self):
        from fastapi import WebSocketDisconnect

        from app.features.ws.router import todo_websocket

        mock_ws = AsyncMock()
        mock_ws.receive_text = AsyncMock(side_effect=WebSocketDisconnect())
        mock_db = AsyncMock()

        user = MagicMock()
        user.id = 1
        user.is_active = True
        user.role = "user"

        with (
            patch("app.features.ws.router.decode_token", return_value=1),
            patch(
                "app.features.ws.router.user_service.get_user",
                return_value=user,
            ),
            patch(
                "app.features.ws.router.manager.connect", new_callable=AsyncMock
            ) as mock_connect,
            patch("app.features.ws.router.manager.disconnect") as mock_disconnect,
        ):
            await todo_websocket(
                websocket=mock_ws,
                token="valid.token",
                subscribe_all=False,
                db=mock_db,
            )
            mock_connect.assert_awaited_once_with(mock_ws, 1)
            mock_disconnect.assert_called_once_with(mock_ws, 1)
