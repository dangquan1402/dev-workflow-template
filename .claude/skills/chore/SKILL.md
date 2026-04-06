---
name: chore
description: Start a maintenance task (deps, CI, tooling).
user-invocable: true
---

Start a chore following the lightweight workflow.

## Steps

1. Ask the user for:
   - What maintenance task? (dep update, CI change, tooling)

2. Create the branch:
   ```
   git checkout develop
   git pull origin develop
   git checkout -b chore/{slug}
   ```

3. Do the work:
   - Update dependencies, CI config, or tooling
   - Run tests to verify nothing broke

4. If dependency update:
   - Check for breaking changes in the changelog
   - Note CVE number if this is a security patch
   - Test that the app still builds and runs

5. Create PR with chore template
   - No changelog entry needed unless breaking
   - No doc update needed

6. Commit message format: `chore(scope): description`
