# 1. Adopt Doc-First Development Workflow

Date: 2026-04-06

## Status

Accepted

## Context

Documentation consistently drifts from code because docs are treated as an afterthought. The "write docs later" task never happens. New team members waste days following outdated instructions.

## Decision

We adopt a doc-first workflow where interface documentation (ERD, API contracts, ADRs) is written before implementation code. Different branch types have different documentation obligations enforced by CI and Claude Code hooks.

## Consequences

- Features take slightly longer to start (design phase before coding)
- Documentation stays in sync because it's written first and shipped in the same PR
- New team members can onboard from docs with confidence
- Refactors must prove no behavior change, preventing scope creep
- Hotfixes skip docs to maintain speed, but require post-mortem within 48h
