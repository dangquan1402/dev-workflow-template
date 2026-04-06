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
| `category_id` | integer  | No       | `null`  | Filter by category ID (must belong to the user). |
| `skip`        | integer  | No       | `0`     | Number of results to skip (pagination offset, >= 0). |
| `limit`       | integer  | No       | `20`    | Max results per page (1-100).                    |

### Response

**200 OK** -- Returns `TodoListResponse`:

```json
{
  "items": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "user_id": 5,
      "categories": [
        { "id": 1, "name": "Shopping", "color": "#00ff00", "user_id": 5, "created_at": "...", "updated_at": "..." }
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
