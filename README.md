# claude memory test

Tests how Claude Code resolves `CLAUDE.md` files and `.claude/commands/` from nested directories.

## Structure

Nested directories each override different values in their `CLAUDE.md`. Custom commands (`/level`, `/rootpath`) test command inheritance and visibility across directory levels.

Run `./test-claude-memory.py show` to see the full tree.

## Usage

```
just show   # display tree with all CLAUDE.md and command contents -> show.txt
just run    # run claude from each directory, collect responses -> run.txt
just all    # both
```

Or directly:

```
./test-claude-memory.py show
./test-claude-memory.py run
./test-claude-memory.py run "custom prompt"
./test-claude-memory.py run --from-root
```
