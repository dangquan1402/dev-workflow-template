---
paths:
  - "app/**/router.py"
---

Check @docs/reference/api/ for existing API contracts before modifying endpoints.
Write or update API contract doc BEFORE changing router code.
Register new routers in app/main.py with prefix `/api/v1/{plural}`.
