# Dev Workflow Template

FastAPI + MVC + RIRO architecture with doc-first development workflow.

## Where to Find Things

| Need | Read | Loaded |
|---|---|---|
| Code templates | @docs/reference/architecture/templates.md | When touching `app/features/**` |
| Layer rules | @docs/reference/architecture/layer-rules.md | When touching `app/features/**` |
| Naming conventions | @docs/reference/architecture/naming.md | When touching `app/features/**` |
| Database schema | @docs/reference/erd.md | When touching models or alembic |
| API contracts | @docs/reference/api/*.md | When touching routers |
| Docker / Makefile | @docs/reference/infrastructure.md | On demand |
| Git workflow & PR flow | @docs/reference/git-workflow.md | When branching or creating PRs |
| Architecture decisions | @docs/decisions/*.md | On demand |

## Branching Model

**`main`** = production. **`develop`** = integration. See @docs/reference/git-workflow.md.

| Prefix | Base | Commit prefix | SemVer |
|---|---|---|---|
| `feature/*` | `develop` | `feat(scope):` | MINOR |
| `bugfix/*` | `develop` | `fix(scope):` | PATCH |
| `hotfix/*` | `main` | `fix(scope):` | PATCH |
| `refactor/*` | `develop` | `refactor(scope):` | None |
| `chore/*` | `develop` | `chore(scope):` | None |

Branch naming: `{type}/GH-{issue}-{slug}`

## Doc-First Rules

- **feature:** ERD + API contract BEFORE code. Docs in same PR.
- **bugfix:** Regression test FIRST. Minimal fix. Root cause in PR.
- **hotfix:** Ship first. Post-mortem ADR within 48h.
- **refactor:** ADR justifying why. All tests pass. No behavior change.
- **chore:** Tests pass. Note CVE if security.

## Doc Scaling Rules

- Each doc file: max 150 lines
- If exceeded: convert to folder with `index.md` (30 lines) + sub-pages
- CLAUDE.md: max 60 lines (this file — routing map only)
- Do NOT scan the repo for patterns — use docs and rules

## Skills

`/new-feature` `/bugfix` `/hotfix` `/refactor` `/chore`
