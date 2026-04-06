# WebSocket API — Todo Notifications

## Connection

```
ws://host/ws/todos?token=<access_token>
```

Authentication is via query parameter `token` (JWT access token), since WebSocket connections do not support custom HTTP headers in the browser.

### Authentication Flow

1. Client connects with `?token=<access_token>`
2. Server validates the JWT token (must be type `access`)
3. Server verifies the user exists and is active
4. On success: connection is accepted
5. On failure: connection is closed with code `4001` and a reason string

### Admin Subscription

Admin users (role `admin`) may pass `?subscribe_all=true` to receive events for **all** users. Regular users always receive only their own events regardless of this parameter.

## Events

All messages are JSON objects with the following structure:

```json
{
  "event": "<event_type>",
  "data": { ... }
}
```

### Event Types

| Event           | Trigger                        | Data                  |
|-----------------|--------------------------------|-----------------------|
| `todo.created`  | A todo is created              | Full `TodoResponse`   |
| `todo.updated`  | A todo is updated              | Full `TodoResponse`   |
| `todo.deleted`  | A todo is soft-deleted         | Full `TodoResponse`   |

### Data Schema

The `data` field contains a serialized `TodoResponse`:

```json
{
  "id": 1,
  "title": "Buy milk",
  "description": null,
  "status": "pending",
  "user_id": 42,
  "categories": [],
  "created_at": "2026-04-06T12:00:00",
  "updated_at": "2026-04-06T12:00:00"
}
```

## Error Codes

| Code | Reason           | Description                          |
|------|------------------|--------------------------------------|
| 4001 | Invalid token    | Token is missing, expired, or invalid|
| 4001 | Invalid user     | User not found or inactive           |

## Keep-Alive

The server keeps the connection open by waiting for incoming messages. The client should send periodic pings (or any text message) to keep the connection alive. The server does not echo back client messages.
