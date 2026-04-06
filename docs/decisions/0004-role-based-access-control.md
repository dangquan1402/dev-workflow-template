# 4. Role-Based Access Control

Date: 2026-04-06

## Status

Proposed

## Context

The application has JWT authentication but no authorization. All authenticated users can perform any action, including listing all users and deleting accounts. We need to restrict sensitive operations (user management, deletions) to administrators while keeping profile viewing open to all authenticated users.

## Decision

Add a `role` column to the `users` table with a string enum (`admin`, `user`). Default is `user`. Introduce a `get_current_admin` dependency that wraps `get_current_user` and checks the role. Protect endpoints:

- `GET /api/v1/users` (list) -- admin only
- `DELETE /api/v1/users/{id}` -- admin only
- `PATCH /api/v1/users/{id}` -- owner or admin
- `GET /api/v1/users/{id}` -- any authenticated user

We use a simple string column rather than a separate roles/permissions table because the application currently only needs two roles. A many-to-many permission system would add complexity without current benefit.

## Consequences

- Admin users can manage other users; regular users cannot
- Registration defaults to `user` role -- no self-promotion
- Role is stored as a string column for simplicity and easy migration to a full RBAC table later
- Existing users will receive `user` role via server_default in migration
- API contracts change: `UserResponse` now includes `role`, `UserUpdate` accepts optional `role`
