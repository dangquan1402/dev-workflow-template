---
name: refactor
description: Start a refactor with justification pipeline. Proves no behavior change.
user-invocable: true
---

Start a refactor following the justification pipeline.

## Steps

1. Ask the user for:
   - WHY refactor? (must be a concrete problem, not "cleaner code")
   - Scope: what's changing, what's NOT
   - Target architecture

2. Create the ADR first (before any code):
   Create `docs/decisions/NNNN-{slug}.md`:
   ```markdown
   # NNNN. Refactor: {What}

   Date: {today}

   ## Status
   Proposed

   ## Context
   <!-- What concrete problem does the current structure cause? -->

   ## Decision
   <!-- How will you restructure? -->

   ## Consequences
   <!-- What becomes easier? What gets harder? -->
   ```

3. Create the branch:
   ```
   git checkout develop
   git pull origin develop
   git checkout -b refactor/GH-{issue_number}-{slug}
   ```

4. Before making any changes, snapshot the current state:
   - Run full test suite, record results
   - Note current API contracts (endpoints, request/response shapes)
   - Note current ERD

5. Implement the refactor:
   - Restructure code
   - Do NOT change any behavior
   - Do NOT add features
   - Do NOT change API contracts
   - Do NOT change database schema

6. After refactoring, verify:
   - ALL existing tests pass (same results as snapshot)
   - API contracts unchanged
   - ERD unchanged
   - No new dependencies added (unless justified in ADR)

7. Update internal docs only:
   - Architecture docs if structure changed
   - CLAUDE.md if conventions changed

8. Commit message format: `refactor(scope): description`
