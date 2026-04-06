---
name: hotfix
description: Start an urgent production hotfix. Fast-track process — ship first, document after.
user-invocable: true
---

Start a hotfix following the fast-track process.

## Steps

1. Ask the user for:
   - What is broken in production?
   - User impact (how many affected?)
   - Proposed fix (smallest possible change)

2. Create the branch FROM MAIN (not develop):
   ```
   git checkout main
   git pull origin main
   git checkout -b hotfix/INC-{number}-{slug}
   ```

3. Implement the fix:
   - SMALLEST possible change
   - No refactoring
   - No feature work
   - Touch as few files as possible

4. Verify:
   - Smoke test passes
   - Existing tests pass

5. Ask for rollback plan:
   - "If this fix makes things worse, how do we revert?"
   - Document in PR description

6. Create PR targeting MAIN with the hotfix template

7. Remind the user of post-merge obligations (within 48h):
   - [ ] Write post-mortem ADR in `docs/decisions/`
   - [ ] Add monitoring/alert to prevent recurrence
   - [ ] Cherry-pick to develop: `git checkout develop && git cherry-pick {commit}`
   - [ ] Create follow-up issue if deeper fix needed

8. Commit message format: `fix(scope): description`
