---
name: new-feature
description: Start a new feature with the doc-first pipeline. Creates issue, branch, and doc stubs.
user-invocable: true
---

Start a new feature following the doc-first pipeline.

## Steps

1. Ask the user for:
   - Feature name (short description)
   - Related issue number (or create one)

2. Create the branch:
   ```
   git checkout develop
   git pull origin develop
   git checkout -b feature/GH-{issue_number}-{slug}
   ```

3. Determine doc obligations:
   - Does this feature add new database tables? → Create ERD stub
   - Does this feature add/change API endpoints? → Create API contract stub
   - Is there an architectural decision? → Create ADR stub

4. Create doc stubs as needed:

   If ERD needed, append to `docs/reference/erd.md`:
   ```markdown
   ## {Feature Name} (GH-{issue_number})
   <!-- Define tables, columns, relationships, constraints -->
   ```

   If API contract needed, create `docs/reference/api/{feature-slug}.md`:
   ```markdown
   # {Feature Name} API

   ## Endpoints

   ### POST /api/v1/{resource}

   **Request:**
   ```json
   {}
   ```

   **Response:**
   ```json
   {}
   ```

   **Error codes:**
   | Status | Meaning |
   |---|---|
   | 400 | ... |
   | 404 | ... |
   ```

   If ADR needed, create `docs/decisions/NNNN-{slug}.md`:
   ```markdown
   # NNNN. {Decision Title}

   Date: {today}

   ## Status
   Proposed

   ## Context
   <!-- What is the issue that we're seeing that is motivating this decision? -->

   ## Decision
   <!-- What is the change that we're proposing? -->

   ## Consequences
   <!-- What becomes easier or harder as a result? -->
   ```

5. Report what was created and remind the user:
   - "Fill in the doc stubs BEFORE writing implementation code"
   - "Docs and code must ship in the same PR"
