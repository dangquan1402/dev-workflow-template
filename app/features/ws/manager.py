import uuid

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections per user."""

    def __init__(self):
        self.active_connections: dict[uuid.UUID, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: uuid.UUID):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: uuid.UUID):
        self.active_connections[user_id].remove(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_to_user(self, user_id: uuid.UUID, message: dict):
        """Send message to all connections of a specific user."""
        connections = self.active_connections.get(user_id, [])
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass  # Connection may have closed

    async def broadcast(self, message: dict, exclude_user_id: uuid.UUID | None = None):
        """Send message to all connected users (for admin subscriptions)."""
        for user_id, connections in self.active_connections.items():
            if user_id == exclude_user_id:
                continue
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()
