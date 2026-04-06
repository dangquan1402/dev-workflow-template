# Dev Workflow Template

A doc-first development workflow with branch-type-specific pipelines.

## Branch Types & Conventions

| Prefix | Purpose | Branches from | Merges to |
|---|---|---|---|
| `feature/*` | New functionality | `develop` | `develop` |
| `bugfix/*` | Fix broken behavior | `develop` | `develop` |
| `hotfix/*` | Urgent production fix | `main` | `main` + `develop` |
| `refactor/*` | Restructure, no behavior change | `develop` | `develop` |
| `chore/*` | Deps, CI, tooling | `develop` | `develop` |

Branch naming: `{type}/GH-{issue_number}-{short-description}`
Example: `feature/GH-42-user-auth`

## Commit Convention

Use Conventional Commits:
- `feat(scope): description` — new feature (MINOR bump)
- `fix(scope): description` — bug fix (PATCH bump)
- `refactor(scope): description` — restructure (no bump)
- `chore(scope): description` — maintenance (no bump)
- `docs(scope): description` — documentation only (no bump)
- Add `BREAKING CHANGE:` footer for breaking changes (MAJOR bump)

## Doc-First Rules

### Features (full pipeline)
1. Write ADR in `docs/decisions/` if architectural
2. Update ERD in `docs/reference/erd.md` if new tables
3. Define API contract in `docs/reference/api/` before coding
4. Implement code following base class conventions
5. Update docs in the SAME PR as code — never a follow-up

### Bugfixes (diagnosis-first)
1. Write regression test FIRST (proves the bug exists)
2. Fix with minimal change — no refactoring
3. Document root cause in PR description
4. Update docs ONLY if behavior changed

### Hotfixes (ship first, document after)
1. Minimal patch, smallest possible change
2. Smoke test passes
3. Post-mortem ADR within 48 hours after merge
4. Follow-up issue for deeper fix if needed

### Refactors (prove no behavior change)
1. Write ADR justifying WHY (not "cleaner" — concrete reason)
2. ALL existing tests must pass — zero behavior change
3. No new features smuggled in
4. API contracts unchanged, ERD unchanged
5. Update internal docs only (architecture, CLAUDE.md)

### Chores (lightweight)
1. Tests pass
2. Note CVE number if security-related dependency update
3. No changelog unless breaking

## Documentation Structure (Diátaxis)

```
docs/
  tutorials/       — learning-oriented, step-by-step
  how-to/          — goal-oriented, solve a specific problem
  reference/       — factual, mirrors codebase structure
    api/           — API contracts (OpenAPI or markdown)
    erd.md         — entity-relationship diagram
  explanation/     — understanding-oriented, architecture context
  decisions/       — ADRs (immutable, numbered)
```

## Review Requirements

| Branch type | Reviewers | Doc review? |
|---|---|---|
| `feature/*` | 2 | Yes |
| `bugfix/*` | 1 | Only if behavior changed |
| `hotfix/*` | 1 (senior) | No (post-mortem after) |
| `refactor/*` | 2 | Architecture docs only |
| `chore/*` | 1 | No |

## Available Skills

- `/new-feature` — start a feature branch with full doc-first pipeline
- `/bugfix` — start a bugfix with diagnosis-first workflow
- `/hotfix` — start a hotfix with fast-track process
- `/refactor` — start a refactor with justification pipeline
- `/chore` — start a chore with lightweight workflow
