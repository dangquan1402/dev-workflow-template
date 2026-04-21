# Search API

Full-text search across todos for the authenticated user.

## `GET /api/v1/todos/search`

Search todos by title and description using case-insensitive matching (`ILIKE`).
Results are scoped to the authenticated user only.

### Authentication

Requires a valid JWT access token in the `Authorization: Bearer <token>` header.

### Query Parameters

| Parameter     | Type     | Required | Default | Description                                      |
|---------------|----------|----------|---------|--------------------------------------------------|
| `q`           | string   | Yes      | --      | Search query (min 1 character). Matches against `title` and `description` using `ILIKE`. |
| `status`      | string   | No       | `null`  | Filter by todo status: `pending`, `in_progress`, `done`. |
| `category_id` | uuid     | No       | `null`  | Filter by category ID (must belong to the user). |
| `skip`        | integer  | No       | `0`     | Number of results to skip (pagination offset, >= 0). |
| `limit`       | integer  | No       | `20`    | Max results per page (1-100).                    |

### Response

**200 OK** -- Returns `TodoListResponse`:

```json
{
  "items": [
    {
      "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "categories": [
        { "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e", "name": "Shopping", "color": "#00ff00", "user_id": "550e8400-e29b-41d4-a716-446655440000", "created_at": "...", "updated_at": "..." }
      ],
      "created_at": "2026-04-06T12:00:00",
      "updated_at": "2026-04-06T12:00:00"
    }
  ],
  "total": 1
}
```

**401 Unauthorized** -- Missing or invalid token.

**422 Unprocessable Entity** -- Validation error (e.g., `q` is empty).

### Example

```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/todos/search?q=groceries&status=pending&skip=0&limit=10"
```
