# Entity-Relationship Diagram

Update this file BEFORE writing migrations. The ERD is the spec — code implements it.

```mermaid
erDiagram
    USER {
        uuid id PK
        string email UK
        string name
        string hashed_password
        string role
        bool is_active
        datetime created_at
        datetime updated_at
    }

    TODO {
        uuid id PK
        string title
        string description
        string status
        uuid user_id FK
        datetime created_at
        datetime updated_at
    }

    CATEGORY {
        uuid id PK
        string name
        string color
        uuid user_id FK
        datetime created_at
        datetime updated_at
    }

    TODO_CATEGORIES {
        uuid todo_id FK
        uuid category_id FK
    }

    USER ||--o{ TODO : "has many"
    USER ||--o{ CATEGORY : "has many"
    TODO ||--o{ TODO_CATEGORIES : "tagged with"
    CATEGORY ||--o{ TODO_CATEGORIES : "applied to"
```

## Tables

### users

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK, default uuid4 | |
| email | String | unique, not null, indexed | Login identifier |
| name | String | not null | Display name |
| hashed_password | String | not null | bcrypt hash, never returned in API |
| role | String(20) | not null, default "user" | One of: admin, user |
| is_active | Boolean | not null, default true | Soft delete flag |
| created_at | DateTime | not null, default now() | TimestampMixin |
| updated_at | DateTime | not null, default now(), on update now() | TimestampMixin |

### Indexes

| Table | Columns | Type | Purpose |
|---|---|---|---|
| users | email | unique | Login lookup |
| users | id | primary key | Default |

### todos

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK, default uuid4 | |
| title | String | not null | Short description of the task |
| description | String | nullable | Detailed description |
| status | String | not null, default "pending" | One of: pending, in_progress, done |
| user_id | UUID | FK → users.id, not null, indexed | Owner of the todo |
| created_at | DateTime | not null, default now() | TimestampMixin |
| updated_at | DateTime | not null, default now(), on update now() | TimestampMixin |

### Indexes

| Table | Columns | Type | Purpose |
|---|---|---|---|
| users | email | unique | Login lookup |
| users | id | primary key | Default |
| todos | user_id | index | Filter todos by user |
| todos | status | index | Filter todos by status |
| todos | id | primary key | Default |

### categories

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK, default uuid4 | |
| name | String(100) | not null | Category name |
| color | String(7) | nullable | Hex color code (e.g. #ff0000) |
| user_id | UUID | FK -> users.id, not null, indexed | Owner of the category |
| created_at | DateTime | not null, default now() | TimestampMixin |
| updated_at | DateTime | not null, default now(), on update now() | TimestampMixin |

### todo_categories (junction table)

| Column | Type | Constraints | Description |
|---|---|---|---|
| todo_id | UUID | PK, FK -> todos.id (CASCADE) | |
| category_id | UUID | PK, FK -> categories.id (CASCADE) | |

### Indexes

| Table | Columns | Type | Purpose |
|---|---|---|---|
| users | email | unique | Login lookup |
| users | id | primary key | Default |
| todos | user_id | index | Filter todos by user |
| todos | status | index | Filter todos by status |
| todos | id | primary key | Default |
| categories | user_id | index | Filter categories by user |
| categories | id | primary key | Default |
| todo_categories | (todo_id, category_id) | composite PK | Unique pairing |

### oauth_accounts (GH-23)

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK, default uuid4 | |
| user_id | UUID | FK -> users.id (CASCADE), not null, indexed | Linked local user |
| provider | String(50) | not null | OAuth provider name: "google", "github" |
| provider_user_id | String(255) | not null | User ID from the OAuth provider |
| provider_email | String(255) | nullable | Email from provider (for reference) |
| access_token | String | nullable | Provider access token (encrypted at rest) |
| refresh_token | String | nullable | Provider refresh token (encrypted at rest) |
| created_at | DateTime | not null, default now() | TimestampMixin |
| updated_at | DateTime | not null, default now(), on update now() | TimestampMixin |

**Unique constraint:** `(provider, provider_user_id)` — one account per provider per user.

### Indexes

| Table | Columns | Type | Purpose |
|---|---|---|---|
| oauth_accounts | user_id | index | Find all linked providers for a user |
| oauth_accounts | (provider, provider_user_id) | unique | Prevent duplicate provider links |

<!-- TODO: Add OAUTH_ACCOUNT entity to mermaid diagram above -->

### Future Tables

When adding new features, define tables here BEFORE creating the Alembic migration.
Follow the pattern:
1. Add mermaid entity to the diagram above
2. Add table definition section below
3. Add indexes section
4. Then run: `alembic revision --autogenerate -m "add {table_name}"`
