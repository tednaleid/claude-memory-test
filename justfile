# ABOUTME: Recipes for running claude memory tests.
# ABOUTME: Saves show/run output to files for comparison across claude versions.

setup:
    #!/usr/bin/env bash
    set -euo pipefail
    chmod +x team/team-info.py
    ln -sf ../../team/.claude/commands/report.md .claude/commands/report.md

show: setup
    #!/usr/bin/env bash
    set -euo pipefail
    ./test-claude-memory.py show | tee show.txt

run: setup
    #!/usr/bin/env bash
    set -euo pipefail
    export PATH="$(pwd)/team:$PATH"
    ./test-claude-memory.py run | tee run.txt

all: show run
