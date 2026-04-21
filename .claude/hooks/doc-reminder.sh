#!/bin/bash
# PostToolUse hook: remind about docs when source code is modified
# Only runs when: Edit|Write tool + file is in app/ (via "if" field in settings)
# Skips: docs/, tests/, config files, markdown

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Skip if no file path
[ -z "$FILE" ] && exit 0

# Skip docs, tests, config, markdown — only care about source code
if echo "$FILE" | grep -qE '(docs/|tests/|README|CLAUDE|CHANGELOG|\.md$|\.json$|\.yml$|\.yaml$|\.ini$|\.cfg$|__pycache__)'; then
    exit 0
fi

# Only remind for actual application code (match both relative and absolute paths)
if echo "$FILE" | grep -qE '(/|^)app/'; then
    jq -n --arg file "$(basename "$FILE")" '{
      hookSpecificOutput: {
        hookEventName: "PostToolUse",
        additionalContext: ("Source file modified: " + $file + ". Check if related docs need updating.")
      }
    }'
fi

exit 0
