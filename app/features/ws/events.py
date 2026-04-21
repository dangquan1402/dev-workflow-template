import uuid

from .manager import manager


async def notify_todo_event(user_id: uuid.UUID, event_type: str, todo_data: dict):
    """Send a todo event to the user's WebSocket connections.

    Also broadcasts to admin users who have subscribed to all events.
    """
    message = {
        "event": event_type,
        "data": todo_data,
    }
    await manager.send_to_user(user_id, message)
