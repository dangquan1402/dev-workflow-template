# Git Workflow

## Branches

- **`main`** — production branch. Hotfixes branch from here.
- **`develop`** — integration branch. Features, bugfixes, refactors, and chores branch from here.

## Branch Naming

```
{type}/GH-{issue}-{slug}
```

| Type | Base branch | Commit prefix | SemVer |
|------|------------|--------------|--------|
| `feature/` | `develop` | `feat(scope):` | MINOR |
| `bugfix/` | `develop` | `fix(scope):` | PATCH |
| `hotfix/` | `main` | `fix(scope):` | PATCH |
| `refactor/` | `develop` | `refactor(scope):` | None |
| `chore/` | `develop` | `chore(scope):` | None |

Examples: `feature/GH-42-user-avatars`, `bugfix/GH-58-login-redirect`, `hotfix/INC-12-payment-crash`

## PR Flow

1. **Checkout** from the correct base branch:
   ```bash
   git checkout {base}       # main or develop
   git pull origin {base}
   git checkout -b {type}/GH-{issue}-{slug}
   ```

2. **Work** — commit with conventional prefix (`feat(scope):`, `fix(scope):`, etc.)

3. **Before PR** — rebase onto latest base:
   ```bash
   git fetch origin
   git rebase origin/{base}
   ```

4. **Resolve conflicts** if any, then push:
   ```bash
   git push -u origin {branch} --force-with-lease
   ```

5. **Create PR** targeting the base branch. Use the matching template from `.github/PULL_REQUEST_TEMPLATE/`.

6. **Link issues** — use `Closes #N` or `Fixes #N` in the PR description.

7. **Merge** — squash or merge commit.

## Doc-First Rules

- **feature/** — ERD + API contract BEFORE code. Docs in same PR.
- **bugfix/** — Regression test FIRST. Minimal fix. Root cause in PR.
- **hotfix/** — Ship first. Post-mortem ADR within 48h.
- **refactor/** — ADR justifying why. All tests pass. No behavior change.
- **chore/** — Tests pass. Note CVE if security.

## Release Flow

1. PRs merge into `develop`
2. When ready to release: merge `develop` → `main`
3. Tag the release on `main`
4. Hotfixes go directly to `main`, then cherry-pick back to `develop`

## Skills

Each branch type has a matching skill that guides the full workflow:

| Skill | What it does |
|-------|-------------|
| `/new-feature` | Doc-first: ERD + API contract → code → PR |
| `/bugfix` | Diagnosis-first: regression test → minimal fix → PR |
| `/hotfix` | Fast-track: smallest fix → PR → post-mortem later |
| `/refactor` | Justification: ADR → restructure → prove no behavior change |
| `/chore` | Lightweight: update → test → PR |
