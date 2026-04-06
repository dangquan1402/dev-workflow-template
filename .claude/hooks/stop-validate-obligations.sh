#!/bin/bash
# Stop hook: validate branch-type obligations before session ends
# Zero cost when everything is fine (exit 0, no output)
# Blocks stop + sends reason when obligations are missing

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

# --- Skip validation for branches with no obligations ---
case "$BRANCH" in
    main|develop|unknown)
        exit 0 ;;
    chore/*)
        exit 0 ;;
esac

# --- Gather what changed (uncommitted + staged) ---
CHANGED=$(git diff --name-only HEAD 2>/dev/null; git diff --name-only --cached 2>/dev/null)
[ -z "$CHANGED" ] && exit 0  # nothing changed, nothing to validate

HAS_SRC=$(echo "$CHANGED" | grep -E '^app/' | head -1)
HAS_DOCS=$(echo "$CHANGED" | grep -E '^docs/' | head -1)
HAS_TESTS=$(echo "$CHANGED" | grep -E '^tests/' | head -1)
HAS_MIGRATION=$(echo "$CHANGED" | grep -iE '(alembic/versions|migration)' | head -1)
SRC_COUNT=$(echo "$CHANGED" | grep -cE '^app/' || echo 0)

# --- Branch-type-specific checks ---
PROBLEMS=""

case "$BRANCH" in
    feature/*)
        if [ -n "$HAS_SRC" ] && [ -z "$HAS_DOCS" ]; then
            PROBLEMS="Feature branch has source changes in app/ but no updates in docs/. Check if docs/reference/api/ or docs/reference/erd.md need updating."
        fi
        ;;
    bugfix/*)
        if [ -n "$HAS_SRC" ] && [ -z "$HAS_TESTS" ]; then
            PROBLEMS="Bugfix branch has source changes but no test updates. A regression test should be written first to prove the bug exists."
        fi
        ;;
    hotfix/*)
        if [ "$SRC_COUNT" -gt 5 ]; then
            PROBLEMS="Hotfix touches $SRC_COUNT source files. Hotfixes should be minimal — the smallest change that stops the bleeding."
        fi
        ;;
    refactor/*)
        if [ -n "$HAS_MIGRATION" ]; then
            PROBLEMS="Refactor branch includes migration files. Refactors must not change the database schema — use a feature/ branch instead."
        fi
        ;;
esac

# --- Output ---
if [ -z "$PROBLEMS" ]; then
    exit 0  # all good, no output, no cost
else
    # Block Claude from stopping, send reason back
    jq -n --arg reason "$PROBLEMS" '{
      hookSpecificOutput: {
        hookEventName: "Stop",
        decision: "block",
        reason: $reason
      }
    }'
    exit 0
fi
