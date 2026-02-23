#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# ABOUTME: Tests how claude loads CLAUDE.md files from different directories.
# ABOUTME: Finds all dirs with CLAUDE.md, shows contents, and queries claude with a prompt.

import argparse
import json
import os
import subprocess
import sys
import textwrap
from collections.abc import Callable
from pathlib import Path

# Entry is (label, content_str) for static or (label, callable) for deferred
type Entry = tuple[str, str | Callable[[], str]]


def find_claude_md_dirs(root: Path) -> list[Path]:
    """Find all directories containing CLAUDE.md, sorted by depth then name."""
    dirs = [f.parent for f in root.rglob("CLAUDE.md") if ".git" not in f.parts]
    return sorted(dirs, key=lambda d: (len(d.parts), d))


def build_tree(dirs: list[Path], root: Path) -> dict:
    """Build a nested dict representing the directory tree."""
    tree: dict = {}
    for d in dirs:
        relative = d.relative_to(root)
        parts = relative.parts if str(relative) != "." else ()
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
    return tree


def read_content(path: Path) -> str:
    """Read file contents, ensuring it ends with a newline."""
    content = path.read_text()
    if not content.endswith("\n"):
        content += "\n"
    return content


def print_indented(text: str, prefix: str) -> None:
    """Print each line of text with a prefix."""
    for line in text.splitlines():
        print(f"{prefix}  {line}")


def static_entries(current_path: Path) -> list[Entry]:
    """Collect file-based entries for a directory node."""
    entries: list[Entry] = []
    claude_md = current_path / "CLAUDE.md"
    level_md = current_path / ".claude" / "commands" / "level.md"
    rootpath_md = current_path / ".claude" / "commands" / "rootpath.md"
    report_md = current_path / ".claude" / "commands" / "report.md"
    team_info = current_path / "team-info.py"

    if claude_md.exists():
        entries.append(("CLAUDE.md", read_content(claude_md)))
    if level_md.exists():
        entries.append((".claude/commands/level.md", read_content(level_md)))
    if rootpath_md.exists():
        entries.append((".claude/commands/rootpath.md", read_content(rootpath_md)))
    if report_md.exists():
        label = ".claude/commands/report.md"
        if report_md.is_symlink():
            target = os.readlink(report_md)
            label += f" -> {target}"
        entries.append((label, read_content(report_md)))
    if team_info.exists():
        entries.append(("team-info.py", read_content(team_info)))

    return entries


def show_tree(
    tree: dict,
    root: Path,
    current_path: Path,
    prefix: str = "",
    extra_fn: Callable[[Path], list[Entry]] | None = None,
) -> None:
    """Render the tree with file contents, styled like `tree` output."""
    children = sorted(tree.keys())
    file_entries = static_entries(current_path)
    has_claude_md = (current_path / "CLAUDE.md").exists()
    extra_entries: list[Entry] = []
    if extra_fn and has_claude_md:
        extra_entries = extra_fn(current_path)

    all_entries = file_entries + extra_entries
    total_items = len(all_entries) + len(children)
    item_index = 0

    # Print all entries (static files print content immediately, deferred flush then wait)
    for label, content in all_entries:
        item_index += 1
        is_last = (item_index == total_items)
        connector = "└── " if is_last else "├── "
        continuation = "    " if is_last else "│   "
        label_col = len(prefix) + len(connector)
        wrap_width = max(80 - label_col, 20)
        wrapped = textwrap.wrap(label, width=wrap_width)
        print(f"{prefix}{connector}{wrapped[0]}")
        label_padding = " " * (label_col - len(prefix) - len(continuation))
        for wrap_line in wrapped[1:]:
            print(f"{prefix}{continuation}{label_padding}{wrap_line}")
        sys.stdout.flush()
        if callable(content):
            content = content()
        print_indented(content.strip(), f"{prefix}{continuation}")
        sys.stdout.flush()

    # Print child directories
    for child in children:
        item_index += 1
        is_last = (item_index == total_items)
        connector = "└── " if is_last else "├── "
        continuation = "    " if is_last else "│   "
        print(f"{prefix}{connector}{child}/")
        sys.stdout.flush()
        show_tree(
            tree[child], root, current_path / child,
            prefix + continuation, extra_fn,
        )


def run_claude_prompt(directory: Path, prompt: str, from_root: bool) -> str:
    """Run claude with a prompt and return its stdout."""
    if from_root:
        target = directory / "answer.txt"
        file_prompt = f'{prompt} Write the answer to {target}.'
        result = subprocess.run(
            ["claude", "-p", file_prompt, "--allowedTools", "Write"],
            capture_output=True,
            text=True,
        )
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        if target.exists():
            return target.read_text()
        return result.stdout or ""
    else:
        result = subprocess.run(
            ["claude", "-p", prompt],
            cwd=directory,
            capture_output=True,
            text=True,
        )
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.stdout or ""


REPORT_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "team_name": {"type": "string"},
        "favorite_color": {"type": "string"},
        "favorite_movie": {"type": "string"},
        "temperature": {"type": "string"},
        "team_script_output": {"type": "string"},
        "level": {"type": "string"},
        "rootpath": {"type": "string"},
    },
    "required": ["name", "team_name", "favorite_color", "favorite_movie",
                  "temperature", "team_script_output", "level", "rootpath"],
})


def run_claude_command(directory: Path, command: str) -> str:
    """Run a claude slash command and return its stdout."""
    result = subprocess.run(
        ["claude", "-p", command,
         "--allowedTools", "Bash(git rev-parse*)",
         "--allowedTools", "Bash(*team-info*)",
         "--output-format", "json",
         "--json-schema", REPORT_SCHEMA],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    output = result.stdout or ""
    # --output-format json wraps the result in a JSON envelope; extract the text
    try:
        envelope = json.loads(output)
        structured = envelope.get("structured_output")
        if structured:
            return json.dumps(structured) if isinstance(structured, dict) else str(structured)
        return envelope.get("result", output)
    except (json.JSONDecodeError, AttributeError):
        return output


def main():
    parser = argparse.ArgumentParser(
        description="Test how claude loads CLAUDE.md from different directories"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("show", help="Show directory tree with CLAUDE.md contents")

    run_parser = subparsers.add_parser("run", help="Run claude in each directory")
    run_parser.add_argument(
        "--from-root", action="store_true",
        help="Run claude from root dir, writing answer.txt in each subdirectory",
    )

    args = parser.parse_args()
    root = Path.cwd()

    dirs = find_claude_md_dirs(root)
    if not dirs:
        print("No CLAUDE.md files found.", file=sys.stderr)
        sys.exit(1)

    tree = build_tree(dirs, root)
    print(".")

    if args.command == "show":
        show_tree(tree, root, root)
    elif args.command == "run":
        team_dir = root / "team"

        def get_extras(directory: Path) -> list[Entry]:
            if directory == team_dir:
                return []
            return [
                ("/report:",
                 lambda d=directory: run_claude_command(
                     d, "Execute the /report command")),
            ]
        show_tree(tree, root, root, extra_fn=get_extras)


if __name__ == "__main__":
    main()
