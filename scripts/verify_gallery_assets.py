#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0
"""Verify each demo page references an existing preview asset."""
from __future__ import annotations

import re
import sys
from pathlib import Path

PREVIEW_RE = re.compile(r"!\[preview\]\(([^)]+)\)")
INSIGHT_PREVIEW_REL = Path("docs/alpha_agi_insight_v1/assets/preview.svg")
INSIGHT_PREVIEW_SOURCE_REL = Path("docs/alpha_factory_v1/demos/alpha_agi_insight_v1/assets/preview.svg")


def collect_missing_preview_assets(repo_root: Path) -> list[str]:
    """Return missing/invalid demo preview asset references."""
    demos_dir = repo_root / "docs" / "demos"
    missing: list[str] = []

    for md_file in sorted(demos_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        m = PREVIEW_RE.search(text)
        if not m:
            missing.append(f"{md_file.relative_to(repo_root)}: missing preview")
            continue
        rel = Path(m.group(1).split("#", 1)[0])
        target = (md_file.parent / rel).resolve()
        if md_file.name == "README.md":
            expected_dir = repo_root / "docs" / "demos" / "assets"
        else:
            expected_dir = repo_root / "docs" / md_file.stem / "assets"
        if not target.is_file() or not target.is_relative_to(expected_dir):
            missing.append(f"{md_file.relative_to(repo_root)}: {target.relative_to(repo_root)}")
    return missing


def collect_preview_sync_contract_violations(repo_root: Path) -> list[str]:
    """Return sync-contract violations for shared preview assets."""
    missing: list[str] = []
    preview = repo_root / INSIGHT_PREVIEW_REL
    source = repo_root / INSIGHT_PREVIEW_SOURCE_REL

    if not source.is_file():
        missing.append(f"missing source preview: {INSIGHT_PREVIEW_SOURCE_REL}")
        return missing
    if not preview.is_file():
        missing.append(f"missing mirrored preview: {INSIGHT_PREVIEW_REL}")
        return missing
    if preview.read_text(encoding="utf-8") != source.read_text(encoding="utf-8"):
        missing.append(f"preview mismatch: {INSIGHT_PREVIEW_REL} differs from {INSIGHT_PREVIEW_SOURCE_REL}")
    return missing


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    missing = collect_missing_preview_assets(repo_root)
    missing.extend(collect_preview_sync_contract_violations(repo_root))
    if missing:
        print("Missing preview assets:", file=sys.stderr)
        for item in missing:
            print(f"  {item}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
