# OAuth2 Authentication API (GH-23)

Base path: `/api/v1/auth/oauth`

## Endpoints

### GET /api/v1/auth/oauth/{provider}/authorize

Initiate OAuth2 flow. Returns the provider's authorization URL.

**Path params:**
- `provider` — `google` or `github`

**Response (200 OK):**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&scope=...&state=..."
}
```

**Errors:**
| Status | Condition |
|---|---|
| 400 | Unsupported provider |

---

### GET /api/v1/auth/oauth/{provider}/callback

OAuth2 callback endpoint. Exchanges the authorization code for tokens, creates or links the user account, and returns JWT tokens.

**Path params:**
- `provider` — `google` or `github`

**Query params:**
- `code` — authorization code from provider
- `state` — CSRF state token

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "is_new_user": true
}
```

**Errors:**
| Status | Condition |
|---|---|
| 400 | Missing code or state, or unsupported provider |
| 401 | Invalid or expired authorization code |
| 409 | Provider email already linked to a different account |

---

### GET /api/v1/auth/oauth/providers

List available OAuth2 providers.

**Response (200 OK):**
```json
{
  "providers": ["google", "github"]
}
```

---

### GET /api/v1/auth/oauth/accounts

List OAuth2 accounts linked to the current user. Requires authentication.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "accounts": [
    {
      "id": "d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f80",
      "provider": "google",
      "provider_email": "user@gmail.com",
      "created_at": "2026-04-06T12:00:00Z"
    }
  ]
}
```

---

### DELETE /api/v1/auth/oauth/accounts/{account_id}

Unlink an OAuth2 provider from the current user. Requires authentication. Fails if it would leave the user with no login method (no password and no other OAuth links).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

**Errors:**
| Status | Condition |
|---|---|
| 400 | Cannot unlink — would leave user with no login method |
| 404 | OAuth account not found or not owned by user |

---

## Account Linking Logic

1. User initiates OAuth2 flow via `/authorize`
2. Provider redirects to `/callback` with authorization code
3. Backend exchanges code for provider tokens and fetches user profile
4. **If provider email matches an existing user** → link OAuth account to that user
5. **If no match** → create new user from provider profile, then link
6. **If provider account already linked to a different user** → return 409
7. Return JWT tokens (same format as email/password login)

## Schema Summary

| Schema | Used in | Fields |
|---|---|---|
| `OAuthAuthorizeResponse` | GET /authorize response | authorization_url |
| `OAuthCallbackResponse` | GET /callback response | access_token, refresh_token, token_type, is_new_user |
| `OAuthProvidersResponse` | GET /providers response | providers |
| `OAuthAccountResponse` | GET /accounts response item | id, provider, provider_email, created_at |
| `OAuthAccountsListResponse` | GET /accounts response | accounts |

## Notes

- OAuth2 state parameter must be validated to prevent CSRF
- Provider client IDs and secrets come from environment variables
- Google scopes: `openid email profile`
- GitHub scopes: `user:email`
- Provider access/refresh tokens stored encrypted; only used for initial profile fetch unless future features need ongoing access
