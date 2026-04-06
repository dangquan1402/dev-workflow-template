# Todo API Contract

Base path: `/api/v1/todos`

## Endpoints

### POST /api/v1/todos

Create a new todo.

**Request:**
```json
{
  "title": "Write unit tests",
  "description": "Cover the user service layer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (201 Created):**
```json
{
  "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "title": "Write unit tests",
  "description": "Cover the user service layer",
  "status": "pending",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-04-06T12:00:00Z",
  "updated_at": "2026-04-06T12:00:00Z"
}
```

**Errors:**
| Status | Condition |
|---|---|
| 404 | user_id does not exist |
| 422 | Missing required fields |

---

### GET /api/v1/todos

List todos with pagination and filtering.

**Query Parameters:**
| Param | Type | Default | Description |
|---|---|---|---|
| skip | int | 0 | Offset |
| limit | int | 20 | Max items (cap at 100) |
| user_id | uuid | null | Filter by owner |
| status | string | null | Filter by status: pending, in_progress, done |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
      "title": "Write unit tests",
      "description": "Cover the user service layer",
      "status": "pending",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-04-06T12:00:00Z",
      "updated_at": "2026-04-06T12:00:00Z"
    }
  ],
  "total": 1
}
```

---

### GET /api/v1/todos/{id}

Get a single todo by ID.

**Response (200 OK):** Same as single item in list response.

**Errors:**
| Status | Condition |
|---|---|
| 404 | Todo not found |

---

### PATCH /api/v1/todos/{id}

Update todo fields. Only provided fields are updated.

**Request:**
```json
{
  "status": "in_progress"
}
```

**Response (200 OK):** Updated todo object.

**Errors:**
| Status | Condition |
|---|---|
| 404 | Todo not found |
| 422 | Invalid status value |

---

### DELETE /api/v1/todos/{id}

Hard-delete a todo.

**Response (200 OK):** Deleted todo object.

**Errors:**
| Status | Condition |
|---|---|
| 404 | Todo not found |

---

## Schema Summary

| Schema | Used in | Fields |
|---|---|---|
| `TodoCreate` | POST body | title, description?, user_id |
| `TodoUpdate` | PATCH body | title?, description?, status? |
| `TodoResponse` | All responses | id, title, description, status, user_id, created_at, updated_at |
| `TodoListResponse` | GET list | items: TodoResponse[], total: int |
| `TodoFilter` | GET query params | user_id?, status? |

## Notes

- Status values: `pending`, `in_progress`, `done`
- Default status on creation: `pending`
- Hard delete (not soft delete — unlike users)
- `user_id` must reference an existing user (FK constraint)
- Filtering by status and user_id can be combined
