---
paths:
  - "alembic/**"
  - "app/**/models.py"
---

Check @docs/reference/erd.md before adding or modifying tables.
Update ERD doc BEFORE writing migrations or models.
Run `make migrate-create msg="description"` after creating models.
