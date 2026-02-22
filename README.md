# claude memory test

Tests how Claude Code resolves `CLAUDE.md` files and `.claude/commands/` from nested directories.

## Structure

Nested directories each override different values in their `CLAUDE.md`. Custom commands (`/level`, `/rootpath`, `/report`) test command inheritance and visibility across directory levels.

A `team/` directory simulates a shared "team repo" pattern — holding common config, commands, and scripts that apply across sibling repos. The root `CLAUDE.md` uses `@team/CLAUDE.md` to include shared properties (name, team_name), while local properties (color, movie, temperature) override per directory level.

Run `just show` to see the full tree, or `just run` to invoke claude at each level.

## Team Repo Pattern

The `team/` directory contains:
- `CLAUDE.md` — shared properties included via `@team/CLAUDE.md`
- `team-info.py` — shared script callable from any directory level
- `.claude/commands/report.md` — shared `/report` command, symlinked into root `.claude/commands/`

The symlink is created by `just setup` (run automatically before `show`/`run`). This mirrors a real-world pattern where `team/` is a separate repo and symlinks are created after checkout.

**Real-world note**: In this single-git-repo test, commands inherit from parent `.claude/commands/` directories. In a real multi-repo workspace with separate git repos, commands/skills/agents do NOT traverse parent directories — you'd need `--add-dir`, `~/.claude/commands/` symlinks, or plugins.

## What This Tests

| Feature | How it's tested |
|---------|----------------|
| `@-include` in CLAUDE.md | `name` and `team_name` come from team/CLAUDE.md via @-include |
| `@-include` override precedence | team has color=Teal, root has color=Red after the include |
| CLAUDE.md inheritance | `color`, `movie`, `temp` overridden per level; `name`/`team_name` inherited |
| Shared command via symlink | `/report` symlinked from team/, inherited by subdirectories |
| Team script path resolution | `/report` runs `team/team-info.py` from any CWD |
| Command override | `/level` returns different value per directory |
| Command inheritance | `/rootpath` defined at root, works from all levels |

## Usage

```
just setup  # create symlinks, chmod (run automatically by show/run)
just show   # display tree with all CLAUDE.md and command contents -> show.txt
just run    # run claude from each directory, collect responses -> run.txt
just all    # both
```

Or directly:

```
./test-claude-memory.py show
./test-claude-memory.py run
./test-claude-memory.py run --from-root
```
