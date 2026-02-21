# ABOUTME: Recipes for running claude memory tests.
# ABOUTME: Saves show/run output to files for comparison across claude versions.

show:
    #!/usr/bin/env bash
    set -euo pipefail
    ./test-claude-memory.py show | tee show.txt

run:
    #!/usr/bin/env bash
    set -euo pipefail
    ./test-claude-memory.py run | tee run.txt

all: show run
