# Auth API Contract

Base path: `/api/v1/auth`

## Endpoints

### POST /api/v1/auth/register

Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "name": "Jane Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
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
| 409 | Email already registered |
| 422 | Invalid email format or missing fields |

---

### POST /api/v1/auth/login

Authenticate with email/password, receive JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:**
| Status | Condition |
|---|---|
| 401 | Invalid email or password |

---

### POST /api/v1/auth/refresh

Refresh an expired access token using a valid refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:**
| Status | Condition |
|---|---|
| 401 | Invalid or expired refresh token |

---

### GET /api/v1/auth/me

Get the currently authenticated user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
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
| 401 | Missing or invalid token |

---

## Authentication Dependency

Protected endpoints use `Authorization: Bearer <token>` header.

```python
current_user: User = Depends(get_current_user)
```

Returns 401 if token is missing, expired, or invalid.

---

## Token Details

| Property | Access Token | Refresh Token |
|---|---|---|
| Lifetime | 30 minutes | 7 days |
| Payload `sub` | user ID | user ID |
| Payload `type` | `"access"` | `"refresh"` |

---

## Schema Summary

| Schema | Used in | Fields |
|---|---|---|
| `RegisterRequest` | POST /register body | email, password, name |
| `LoginRequest` | POST /login body | email, password |
| `TokenResponse` | POST /login response | access_token, refresh_token, token_type |
| `RefreshRequest` | POST /refresh body | refresh_token |
| `RefreshResponse` | POST /refresh response | access_token, token_type |

## Notes

- Reuses existing `UserResponse` schema for registration and /me responses
- Passwords are hashed with bcrypt before storage
- JWT signed with HS256 using `SECRET_KEY` from environment
- Refresh tokens use the same signing key but with `type: "refresh"` in payload
- Inactive users (`is_active=false`) are rejected at login
