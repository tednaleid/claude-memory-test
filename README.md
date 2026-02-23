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

**Real-world note**: In this single-git-repo test, commands inherit from parent `.claude/commands/` directories. In a real multi-repo workspace with separate git repos, commands/skills/agents do NOT traverse parent directories — you'd need `--add-dir`, `~/.claude/commands/` symlinks, or plugins.

## Manual Testing (recommended)

The most reliable way to test is interactively. `cd` into any directory and run `claude`, then:

```
Execute the /report command
```

This works correctly at all directory levels because interactive mode prompts for external @-include approval on first use. The `/report` command will:
- Extract all `# Known Facts` from CLAUDE.md context (including @-included values)
- Run `team-info.py` to verify script path resolution
- Reference the `/level` command (Claude loads it as a skill automatically)
- Compute the rootpath via `git rev-parse`

### Known limitation: `claude -p` and external @-includes

The automated `just run` uses `claude -p` (non-interactive/headless mode). External `@-includes` in CLAUDE.md (like `@team/CLAUDE.md`) require a one-time approval prompt that only appears in interactive mode. Once approved, the approval persists across interactive sessions for the same project. However, `-p` mode never triggers the approval flow, so external @-include content is silently dropped.

This means `just run` produces unreliable results for `name` and `team_name` (which come from the @-include). Values defined directly in each directory's own CLAUDE.md (color, movie, temperature) work fine, as do commands, script execution, and CLAUDE.md inheritance from parent directories.

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

Or directly:

```
./test-claude-memory.py show
./test-claude-memory.py run
./test-claude-memory.py run --from-root
```
