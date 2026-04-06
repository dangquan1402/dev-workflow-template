# Dev Workflow Template

A doc-first development workflow with branch-type-specific pipelines, enforced by Claude Code hooks and GitHub Actions.

## Quick Start

```bash
# Clone and start working
git clone https://github.com/dangquan1402/dev-workflow-template
cd dev-workflow-template

# Start a new feature (with Claude Code)
# /new-feature

# Start a bugfix
# /bugfix

# Start a hotfix
# /hotfix
```

## Branch Types

| Prefix | Purpose | Doc obligation |
|---|---|---|
| `feature/*` | New functionality | ADR + ERD + API spec (before coding) |
| `bugfix/*` | Fix broken behavior | Root cause + regression test |
| `hotfix/*` | Urgent production fix | Post-mortem ADR (within 48h) |
| `refactor/*` | Restructure, no behavior change | ADR justifying why |
| `chore/*` | Deps, CI, tooling | None |

## Documentation Structure (Diátaxis)

```
docs/
  tutorials/       — learning-oriented, step-by-step
  how-to/          — goal-oriented, solve a problem
  reference/       — factual, mirrors codebase
    api/           — API contracts
    erd.md         — entity-relationship diagram
  explanation/     — architecture context
  decisions/       — ADRs (numbered, immutable)
```

## What's Included

- **Issue templates** — per branch type (feature, bugfix, hotfix, refactor, chore)
- **PR templates** — per branch type with type-specific checklists
- **Claude Code skills** — `/new-feature`, `/bugfix`, `/hotfix`, `/refactor`, `/chore`
- **Claude Code hooks** — block commits to main/develop, remind about docs, validate obligations at session end
- **GitHub Actions** — auto-label PRs from branch name, enforce branch naming, check docs for features, check rollback plan for hotfixes, block migrations in refactors

## Commit Convention

[Conventional Commits](https://www.conventionalcommits.org/):

```
feat(scope): new feature          → MINOR version bump
fix(scope): bug fix               → PATCH version bump
refactor(scope): restructure      → no version bump
chore(scope): maintenance         → no version bump
docs(scope): documentation only   → no version bump
```

## Philosophy

**Interfaces first, implementation after.**

- ERD, API contracts, ADRs → write before coding
- Business logic, implementation details → the code IS the documentation
- Docs ship in the same PR as code — never a follow-up task
