# Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Feature directory | snake_case | `document_processor` |
| Table name | snake_case, plural | `users`, `ocr_pages` |
| Column name | snake_case | `created_at`, `hashed_password` |
| Model class | PascalCase, singular | `User`, `OcrPage` |
| Schema class | PascalCase + suffix | `UserCreate`, `UserResponse` |
| CRUD instance | lowercase, singular | `user = UserCRUD(User)` |
| Router variable | `router` (in file), `{name}_router` (in main) | `user_router` |
| API prefix | `/api/v1/{plural}` | `/api/v1/users` |
| Branch name | `{type}/GH-{issue}-{slug}` | `feature/GH-42-user-auth` |
| Commit message | `{type}({scope}): description` | `feat(user): add registration` |
