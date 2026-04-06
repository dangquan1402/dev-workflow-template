---
name: bugfix
description: Start a bugfix with diagnosis-first workflow. Creates branch and regression test stub.
user-invocable: true
---

Start a bugfix following the diagnosis-first workflow.

## Steps

1. Ask the user for:
   - Bug description (what's broken?)
   - Related issue number (or create one)
   - Steps to reproduce

2. Create the branch:
   ```
   git checkout develop
   git pull origin develop
   git checkout -b bugfix/GH-{issue_number}-{slug}
   ```

3. Write the regression test FIRST:
   - Ask the user which module/function is affected
   - Create a test file or add a test case that reproduces the bug
   - The test should FAIL at this point (proving the bug exists)

4. Then fix the bug:
   - Make the minimal change needed
   - Do NOT refactor surrounding code
   - Do NOT add features

5. Verify:
   - Run the regression test — it should now pass
   - Run the full test suite — nothing else should break

6. Check doc obligations:
   - Did the fix change user-facing behavior? → Update relevant docs
   - Did the fix NOT change behavior (just fix a crash/error)? → No doc update needed

7. Prepare the PR description with:
   - Root cause explanation
   - What the fix changes
   - Link to the regression test

8. Remind: commit message format is `fix(scope): description`
