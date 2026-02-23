# claude memory test

Tests how Claude Code resolves `CLAUDE.md` files and `.claude/commands/` from nested directories.

## Structure

Nested directories each override different values in their `CLAUDE.md`. Custom commands (`/level`, `/rootpath`, `/report`) test command inheritance and visibility across directory levels.

A `team/` directory simulates a shared "team repo" pattern — holding common config, commands, and scripts that apply across sibling repos. The root `CLAUDE.md` uses `@team/CLAUDE.md` to include shared properties (name, team_name), while local properties (color, movie, temperature) override per directory level.

Run `just show` to see the full tree, or `just run` for automated testing.

## Team Repo Pattern

The `team/` directory contains:
- `CLAUDE.md` — shared properties included via `@team/CLAUDE.md`
- `team-info.py` — shared script callable from any directory level
- `.claude/commands/report.md` — shared `/report` command, symlinked into root `.claude/commands/`

The symlink is created by `just setup` (run automatically before `show`/`run`). This mirrors a real-world pattern where `team/` is a separate repo and symlinks are created after checkout.

Symlinks are necessary as we can't `@-include` them like we can the `team/CLAUDE.md` file in the root `CLAUDE.md`.

### Setup: approving external @-includes

External `@-includes` in CLAUDE.md (like `@team/CLAUDE.md`) require a one-time approval prompt. This prompt only appears in interactive mode — run `claude` interactively once from any directory in the project and accept the "Allow external CLAUDE.md file imports?" prompt. The approval persists for the project and subsequent `claude -p` invocations will respect it. Without this approval, external @-include content is silently dropped.

Neither Claude or I have found where this approval is kept yet, but if I find it, I'll update the script to do this check automatically and be a little smarter about it.

## What This Tests

| Feature | How it's tested |
|---------|----------------|
| `@-include` in CLAUDE.md | `name` and `team_name` come from team/CLAUDE.md via @-include |
| `@-include` override precedence | team has color=Teal, root has color=Red after the include |
| CLAUDE.md inheritance | `color`, `movie`, `temp` overridden per level; `name`/`team_name` inherited |
| Shared command via symlink | `/report` symlinked from team/, inherited by subdirectories |
| Team script path resolution | `/report` runs `team/team-info.py` from any CWD |
| Command cross-referencing | `/report` references `/level` — Claude loads it as a skill |
| Command override | `/level` returns different value per directory |
| Command inheritance | `/rootpath` defined at root, works from all levels |

## Usage

```
just setup  # create symlinks, chmod (run automatically by show/run)
just show   # display tree with all CLAUDE.md and command contents -> show.txt
just run    # run claude -p from each directory, collect responses -> run.txt
just all    # both
```