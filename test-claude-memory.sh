#!/usr/bin/env bash
# ABOUTME: Tests how claude loads CLAUDE.md files from different directories.
# ABOUTME: Iterates subdirectories with CLAUDE.md, showing contents and querying claude.

set -euo pipefail

PROMPT="What is my name, favorite color, and favorite movie?"

# Run from the root directory first
echo "=== . ==="
cat CLAUDE.md
echo "---"
claude -p "$PROMPT"
echo ""

# Then recurse into all subdirectories with CLAUDE.md files
find . -name .git -prune -o -name CLAUDE.md -print0 | while IFS= read -r -d '' file; do
  dir=$(dirname "$file")
  [[ "$dir" == "." ]] && continue
  echo "=== $dir ==="
  cat "$file"
  echo "---"
  (cd "$dir" && claude -p "$PROMPT")
  echo ""
done
