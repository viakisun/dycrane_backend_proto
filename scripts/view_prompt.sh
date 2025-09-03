#!/usr/bin/env bash
set -euo pipefail

PROMPT_PATH="docs/prompts/generate_report_prompt.md"

if [ ! -f "$PROMPT_PATH" ]; then
  echo "Prompt not found: $PROMPT_PATH" >&2
  exit 1
fi

echo "===== BEGIN PROMPT: $PROMPT_PATH ====="
cat "$PROMPT_PATH"
echo
echo "===== END PROMPT ====="
