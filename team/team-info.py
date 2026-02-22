#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# ABOUTME: Shared team script that reports basic environment info.
# ABOUTME: Verifies that team scripts are callable from any directory level.

import os
import subprocess


def main():
    root = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
    cwd = os.getcwd()
    rel = os.path.relpath(cwd, root)
    if rel == ".":
        rel = "root"
    print(f"team-info: called_from={rel}")


if __name__ == "__main__":
    main()
