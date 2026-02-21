#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# ABOUTME: Tests how claude loads CLAUDE.md files from different directories.
# ABOUTME: Finds all dirs with CLAUDE.md, shows contents, and queries claude with a prompt.

import argparse
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path


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


def collect_entries(current_path: Path, extra_fn=None):
    """Collect displayable entries (files + extras) for a directory node."""
    entries = []
    claude_md = current_path / "CLAUDE.md"
    level_md = current_path / ".claude" / "commands" / "level.md"

    if claude_md.exists():
        entries.append(("CLAUDE.md", read_content(claude_md)))
    if level_md.exists():
        entries.append((".claude/commands/level.md", read_content(level_md)))

    if extra_fn and claude_md.exists():
        for label, text in extra_fn(current_path):
            entries.append((label, text))

    return entries


def show_tree(
    tree: dict,
    root: Path,
    current_path: Path,
    prefix: str = "",
    extra_fn: Callable[[Path], list[tuple[str, str]]] | None = None,
) -> None:
    """Render the tree with file contents, styled like `tree` output."""
    children = sorted(tree.keys())
    entries = collect_entries(current_path, extra_fn)

    total_items = len(entries) + len(children)
    item_index = 0

    # Print file entries and extras
    for label, content in entries:
        item_index += 1
        is_last = (item_index == total_items)
        connector = "└── " if is_last else "├── "
        continuation = "    " if is_last else "│   "
        print(f"{prefix}{connector}{label}")
        print_indented(content.strip(), f"{prefix}{continuation}")

    # Print child directories
    for child in children:
        item_index += 1
        is_last = (item_index == total_items)
        connector = "└── " if is_last else "├── "
        continuation = "    " if is_last else "│   "
        print(f"{prefix}{connector}{child}/")
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


def run_claude_command(directory: Path, command: str) -> str:
    """Run a claude slash command and return its stdout."""
    result = subprocess.run(
        ["claude", "-p", command],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.stdout or ""


def main():
    parser = argparse.ArgumentParser(
        description="Test how claude loads CLAUDE.md from different directories"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("show", help="Show directory tree with CLAUDE.md contents")

    run_parser = subparsers.add_parser("run", help="Run claude in each directory")
    DEFAULT_PROMPT = ("What is my name, favorite color, favorite movie,"
                      " and the current temperature? emit only as well formatted"
                      " json with attributes for each value")
    run_parser.add_argument(
        "prompt", nargs="?", default=DEFAULT_PROMPT,
        help="Prompt to send to claude in each directory",
    )
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
        def get_extras(directory: Path) -> list[tuple[str, str]]:
            extras = []
            answer = run_claude_prompt(directory, args.prompt, args.from_root)
            extras.append((f"prompt: {args.prompt}", answer))
            level_md = directory / ".claude" / "commands" / "level.md"
            if level_md.exists():
                response = run_claude_command(directory, "/level")
                extras.append(("/level:", response))
            return extras
        show_tree(tree, root, root, extra_fn=get_extras)


if __name__ == "__main__":
    main()
