#!/bin/bash
# PreToolUse hook: block git commits on main/develop
# Only runs when: Bash tool + command starts with "git commit"

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Skip if not a git commit command
echo "$CMD" | grep -qE '^git commit' || exit 0

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)

if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "develop" ]; then
    echo "Blocked: do not commit directly to $BRANCH. Create a branch first." >&2
    echo "Use: git checkout -b {type}/GH-{issue}-{slug}" >&2
    exit 2
fi

exit 0
