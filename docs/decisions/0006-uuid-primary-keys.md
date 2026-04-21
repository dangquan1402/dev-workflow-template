# 0006. Refactor: Change all IDs from integer to UUID

Date: 2026-04-06

## Status

Proposed

## Context

All primary keys currently use auto-incrementing integers. This exposes:
- **Enumeration attacks** — sequential IDs let attackers guess valid resource URLs
- **Information leakage** — IDs reveal creation order and total record count
- **Distributed unfriendly** — auto-increment requires a single sequence source

## Decision

Replace all `Integer` primary keys and foreign keys with `UUID` (Postgres-native `uuid` type) across every table. UUIDs are generated server-side via `uuid4()` default.

### Scope

- All tables: users, todos, categories, todo_categories, oauth_accounts, comments
- All schemas: response `id` fields become `uuid.UUID`
- All services, routers, CRUD: ID parameters change from `int` to `UUID`
- JWT tokens: subject remains `str(uuid)` (already string-encoded)
- WebSocket manager: keyed by UUID instead of int

### Breaking changes

- API responses: `"id": 1` → `"id": "550e8400-e29b-41d4-a716-446655440000"`
- Path parameters: `/users/1` → `/users/550e8400-...`
- Requires a new migration (drop + recreate for dev)

## Consequences

**Easier:**
- Security — no enumeration, no ordering leaks
- Future distributed/multi-region deployments
- Merging data across environments

**Harder:**
- UUIDs are longer in URLs and logs
- Slightly larger index size (16 bytes vs 4 bytes)
- Existing clients must update to use UUID strings
