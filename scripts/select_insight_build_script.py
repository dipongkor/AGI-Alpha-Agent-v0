#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Select the first available npm build script for the Insight bundle workflow."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

DEFAULT_CANDIDATES = ("build:docs-insight", "build:insight", "build")


def _load_scripts(package_json: Path) -> dict[str, str]:
    payload = json.loads(package_json.read_text(encoding="utf-8"))
    scripts = payload.get("scripts", {})
    if not isinstance(scripts, dict):
        return {}
    return {str(key): str(value) for key, value in scripts.items() if isinstance(value, str)}


def select_build_script(package_json: Path, candidates: tuple[str, ...] = DEFAULT_CANDIDATES) -> str:
    """Return the first candidate script key present in package.json scripts."""
    scripts = _load_scripts(package_json)
    for candidate in candidates:
        command = scripts.get(candidate)
        if command and command.strip():
            return candidate
    raise RuntimeError(f"No supported build script found in {package_json}: tried {', '.join(candidates)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-json", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--print-command", action="store_true")
    args = parser.parse_args(argv)

    try:
        script_name = select_build_script(args.package_json)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(script_name)

    github_output = args.github_output
    if github_output is None:
        output_path = os.getenv("GITHUB_OUTPUT")
        if output_path:
            github_output = Path(output_path)

    if github_output is not None:
        github_output.parent.mkdir(parents=True, exist_ok=True)
        with github_output.open("a", encoding="utf-8") as handle:
            handle.write(f"script={script_name}\n")

    if args.print_command:
        scripts = _load_scripts(args.package_json)
        print(scripts[script_name])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
