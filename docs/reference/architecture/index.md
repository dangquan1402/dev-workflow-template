# Architecture Conventions

## Quick Reference

```
app/
├── main.py                      # Router registration + /health
├── core/                        # Config, security
├── common/                      # Base classes (database, models, crud, pagination)
└── features/{feature_name}/     # One directory per feature
    ├── models.py   → schemas.py → crud.py → service.py → router.py
```

Data flows one direction: **Router → Service → CRUD → Database**

## Detailed Docs

| Doc | Read when | Lines |
|---|---|---|
| [Layer Rules](layer-rules.md) | Understanding what each file does and doesn't do | ~60 |
| [Code Templates](templates.md) | Creating a new feature (copy-paste ready) | ~100 |
| [Naming Conventions](naming.md) | Naming anything (files, tables, classes, routes) | ~30 |

## Minimum Viable Feature

Not every feature needs all files:
- **API-only (no DB):** `router.py` + `schemas.py`
- **Simple CRUD:** all 5 files, use GenericCRUD as-is
- **Complex logic:** all 5 files, custom CRUD queries, service orchestration

## Adding a New Feature

1. Write docs first (ERD, API contract)
2. Use `/new-feature` skill or copy templates from [templates.md](templates.md)
3. Register router in `app/main.py`
4. Register model in `alembic/env.py`
5. Run `make migrate-create msg="add {table}"`
