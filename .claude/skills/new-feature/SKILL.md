---
name: new-feature
description: Start a new feature with the doc-first pipeline. Creates issue, branch, and doc stubs.
user-invocable: true
---

Start a new feature following the doc-first pipeline.

## IMPORTANT: Do NOT scan the repo. All patterns are in CLAUDE.md.

Do not use Glob, Grep, or Read to explore existing features. The code templates
are in CLAUDE.md under "Feature File Templates." Copy them directly, replacing
`{Entity}`, `{entity}`, `{feature_name}`, `{table_name_plural}` with actual names.

## Steps

1. Ask the user for:
   - Feature name (short description)
   - Entity name (e.g., "Product", "Comment")
   - Does it need database tables? (Y/N)
   - Does it have API endpoints? (Y/N)

2. Create the branch:
   ```
   git checkout main
   git pull origin main
   git checkout -b feature/GH-{issue_number}-{slug}
   ```

3. **DOC PHASE (commit first):**

   If database tables needed, append to `docs/reference/erd.md`:
   - Add mermaid entity to the diagram
   - Add table definition with columns, types, constraints
   - Add indexes

   If API endpoints needed, create `docs/reference/api/{feature-slug}.md`:
   - Define each endpoint: method, path, request body, response body, errors
   - Define schema summary table

   If architectural decision, create `docs/decisions/NNNN-{slug}.md`

   Commit the docs: `docs: define {feature} — ERD and API contract before implementation`

4. **CODE PHASE (commit second):**

   Use the templates from CLAUDE.md directly:
   - Create `app/features/{feature_name}/` directory
   - `__init__.py` — empty
   - `models.py` — from CLAUDE.md template
   - `schemas.py` — from CLAUDE.md RIRO template
   - `crud.py` — from CLAUDE.md template, add custom queries
   - `service.py` — from CLAUDE.md template
   - `router.py` — from CLAUDE.md template
   - Register router in `app/main.py`
   - Register model in `alembic/env.py`

   Commit: `feat({feature}): add {feature} with CRUD endpoints`

5. Remind the user:
   - "Fill in the doc stubs BEFORE writing implementation code"
   - "Docs and code ship in the same PR"
   - "Run `make migrate-create msg='add {table}'` after merging"
