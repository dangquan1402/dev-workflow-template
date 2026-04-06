from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.core.security import decode_token
from app.features.user import service as user_service
from app.features.user.models import UserRole

from .manager import manager

router = APIRouter()


@router.websocket("/ws/todos")
async def todo_websocket(
    websocket: WebSocket,
    token: str = Query(...),
    subscribe_all: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """WebSocket endpoint for real-time todo notifications.

    Auth is via query param `token` since WS doesn't support custom headers.
    Admin users can pass `subscribe_all=true` to receive all users' events.
    """
    user_id = decode_token(token, expected_type="access")
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user = await user_service.get_user(db, user_id=user_id)
    if user is None or not user.is_active:
        await websocket.close(code=4001, reason="Invalid user")
        return

    # Only admins can subscribe to all events
    if subscribe_all and user.role != UserRole.admin.value:
        subscribe_all = False

    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
