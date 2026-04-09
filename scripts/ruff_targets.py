#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Resolve tracked Python lint targets and optionally run Ruff."""

from __future__ import annotations

import argparse
import subprocess
import sys
from itertools import islice
from pathlib import Path

PYTHON_FILE_GLOBS: tuple[str, ...] = ("*.py", "*.pyi", "*.ipynb")
DEFAULT_BATCH_SIZE = 200


def _repo_root() -> Path:
    """Return the current Git repository root path."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip())


def list_tracked_python_files(repo_root: Path) -> list[str]:
    """Return tracked Python-related files for Ruff relative to ``repo_root``."""
    command = ["git", "-C", str(repo_root), "ls-files", "-z", "--", *PYTHON_FILE_GLOBS]
    result = subprocess.run(command, check=True, capture_output=True)

    entries = [item for item in result.stdout.decode("utf-8").split("\x00") if item]
    filtered = sorted({entry for entry in entries if not entry.startswith(".git/")})
    return filtered


def run_ruff(repo_root: Path, targets: list[str], batch_size: int) -> int:
    """Run Ruff over ``targets`` in deterministic batches to avoid long argv."""
    if not targets:
        print("No tracked Python files found; skipping Ruff.")
        return 0

    command_prefix = [sys.executable, "-m", "ruff", "check", "--force-exclude"]
    start = 0
    total = len(targets)
    while start < total:
        stop = start + batch_size
        batch = list(islice(targets, start, stop))
        command = command_prefix + batch
        result = subprocess.run(command, cwd=repo_root)
        if result.returncode != 0:
            return result.returncode
        start = stop
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Execute Ruff with the resolved targets.")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Max targets passed to each Ruff invocation when --run is enabled.",
    )
    return parser.parse_args()


def main() -> int:
    """Resolve tracked targets and optionally run Ruff."""
    args = parse_args()
    repo_root = _repo_root()
    targets = list_tracked_python_files(repo_root)

    if args.run:
        return run_ruff(repo_root, targets, batch_size=args.batch_size)

    for target in targets:
        print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
