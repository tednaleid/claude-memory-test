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


def show_tree(
    tree: dict,
    root: Path,
    current_path: Path,
    prefix: str = "",
    extra_fn: Callable[[Path], str | None] | None = None,
) -> None:
    """Render the tree with CLAUDE.md contents, styled like `tree` output."""
    claude_md = current_path / "CLAUDE.md"
    has_claude_md = claude_md.exists()
    children = sorted(tree.keys())
    has_extra = extra_fn is not None and has_claude_md

    # Items after CLAUDE.md: extra block (if any), then children
    remaining_after_md = (1 if has_extra else 0) + len(children)

    # Print CLAUDE.md for this directory if it exists
    if has_claude_md:
        connector = "├── " if remaining_after_md > 0 else "└── "
        continuation = "│   " if remaining_after_md > 0 else "    "
        print(f"{prefix}{connector}CLAUDE.md")
        print_indented(read_content(claude_md), f"{prefix}{continuation}")

    # Print extra content (e.g. claude answer) if provided
    if has_extra:
        extra = extra_fn(current_path)
        connector = "├── " if children else "└── "
        continuation = "│   " if children else "    "
        print(f"{prefix}{connector}answer:")
        if extra:
            print_indented(extra.strip(), f"{prefix}{continuation}")

    # Print child directories
    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)
        connector = "└── " if is_last else "├── "
        continuation = "    " if is_last else "│   "
        print(f"{prefix}{connector}{child}/")
        show_tree(
            tree[child], root, current_path / child,
            prefix + continuation, extra_fn,
        )


def run_claude(directory: Path, prompt: str, from_root: bool) -> str | None:
    """Run claude and return its stdout."""
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
        return result.stdout or None
    else:
        result = subprocess.run(
            ["claude", "-p", prompt],
            cwd=directory,
            capture_output=True,
            text=True,
        )
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.stdout or None


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
        def get_answer(directory: Path) -> str | None:
            return run_claude(directory, args.prompt, args.from_root)
        show_tree(tree, root, root, extra_fn=get_answer)


if __name__ == "__main__":
    main()
