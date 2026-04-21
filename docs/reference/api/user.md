# User API Contract

Base path: `/api/v1/users`

Define endpoints here BEFORE implementing router.py.

## Endpoints

### POST /api/v1/users

Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "Jane Doe"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "Jane Doe",
  "is_active": true,
  "created_at": "2026-04-06T12:00:00Z",
  "updated_at": "2026-04-06T12:00:00Z"
}
```

**Errors:**
| Status | Condition |
|---|---|
| 400 | Email already registered |
| 422 | Invalid email format or missing required fields |

---

### GET /api/v1/users

List users with pagination.

**Query Parameters:**
| Param | Type | Default | Description |
|---|---|---|---|
| skip | int | 0 | Offset |
| limit | int | 20 | Max items (cap at 100) |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "name": "Jane Doe",
      "is_active": true,
      "created_at": "2026-04-06T12:00:00Z",
      "updated_at": "2026-04-06T12:00:00Z"
    }
  ],
  "total": 1
}
```

---

### GET /api/v1/users/{id}

Get a single user by ID.

**Response (200 OK):** Same as single item in list response.

**Errors:**
| Status | Condition |
|---|---|
| 404 | User not found |

---

### PATCH /api/v1/users/{id}

Update user fields. Only provided fields are updated.

**Request:**
```json
{
  "name": "Jane Smith"
}
```

**Response (200 OK):** Updated user object.

**Errors:**
| Status | Condition |
|---|---|
| 404 | User not found |
| 400 | Email already taken (if changing email) |

---

### DELETE /api/v1/users/{id}

Soft-delete a user (sets `is_active = false`).

**Response (200 OK):** Deleted user object.

**Errors:**
| Status | Condition |
|---|---|
| 404 | User not found |

---

## Schema Summary

| Schema | Used in | Fields |
|---|---|---|
| `UserCreate` | POST body | email, password, name |
| `UserUpdate` | PATCH body | name?, email? |
| `UserResponse` | All responses | id, email, name, is_active, created_at, updated_at |
| `UserListResponse` | GET list | items: UserResponse[], total: int |

## Notes

- Password is NEVER returned in any response
- `hashed_password` is stored in DB, not `password`
- Soft delete via `is_active` flag — no hard deletes
- All endpoints will require authentication in the future (except POST for registration)
