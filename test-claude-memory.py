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
from pathlib import Path


def find_claude_md_dirs(root: Path) -> list[Path]:
    """Find all directories containing CLAUDE.md, sorted by depth then name."""
    dirs = [f.parent for f in root.rglob("CLAUDE.md") if ".git" not in f.parts]
    return sorted(dirs, key=lambda d: (len(d.parts), d))


def relative_display(directory: Path) -> str:
    relative = directory.relative_to(Path.cwd())
    return f"./{relative}" if str(relative) != "." else "."


def print_claude_md(directory: Path) -> None:
    """Print the CLAUDE.md file contents with path label and fenced code block."""
    claude_md = directory / "CLAUDE.md"
    relative = directory.relative_to(Path.cwd())
    md_path = f"./{relative}/CLAUDE.md" if str(relative) != "." else "./CLAUDE.md"
    print(f"{md_path}:")
    print("```")
    content = claude_md.read_text()
    if not content.endswith("\n"):
        content += "\n"
    print(content, end="")
    print("```")


def run_claude_local(directory: Path, prompt: str) -> None:
    """Run claude from each directory (cd into it)."""
    display = relative_display(directory)
    print(f"=== {display} ===")
    print_claude_md(directory)

    result = subprocess.run(
        ["claude", "-p", prompt],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    print()


def run_claude_from_root(directory: Path, prompt: str) -> None:
    """Run claude from root, asking it to write answer.txt in the target directory."""
    display = relative_display(directory)
    target = directory / "answer.txt"
    print(f"=== {display} (from root) ===")
    print_claude_md(directory)

    file_prompt = f'{prompt} Write the answer to {target}.'
    result = subprocess.run(
        ["claude", "-p", file_prompt, "--allowedTools", "Write"],
        capture_output=True,
        text=True,
    )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if target.exists():
        print(f"Contents of {target}:")
        print(target.read_text(), end="")
    else:
        print(f"WARNING: {target} was not created")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Test how claude loads CLAUDE.md from different directories"
    )
    parser.add_argument("prompt", help="Prompt to send to claude in each directory")
    parser.add_argument(
        "--from-root", action="store_true",
        help="Run claude from root dir, writing answer.txt in each subdirectory",
    )
    args = parser.parse_args()

    root = Path.cwd()
    dirs = find_claude_md_dirs(root)

    if not dirs:
        print("No CLAUDE.md files found.", file=sys.stderr)
        sys.exit(1)

    for d in dirs:
        if args.from_root:
            run_claude_from_root(d, args.prompt)
        else:
            run_claude_local(d, args.prompt)


if __name__ == "__main__":
    main()
