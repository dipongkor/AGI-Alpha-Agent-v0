# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import re
from pathlib import Path


def _bundle_import_names(bundle_text: str) -> set[str]:
    names: set[str] = set()
    for match in re.finditer(r'import\{([^}]+)\}from"d3"', bundle_text):
        for part in match.group(1).split(","):
            source_name = part.split(" as ")[0].strip()
            if source_name:
                names.add(source_name)
    return names


def _bridge_export_names(bridge_text: str) -> set[str]:
    return set(re.findall(r"^export const ([A-Za-z_$][\w$]*)\s*=\s*d3\.", bridge_text, re.MULTILINE))


def test_docs_d3_bridge_exports_match_bundle_import_surface() -> None:
    bundle_text = Path("docs/alpha_agi_insight_v1/insight.bundle.js").read_text(encoding="utf-8")
    bridge_text = Path("docs/alpha_agi_insight_v1/d3.exports.js").read_text(encoding="utf-8")

    required = _bundle_import_names(bundle_text)
    exported = _bridge_export_names(bridge_text)

    missing = sorted(required - exported)
    assert not missing, f"d3 bridge is missing named exports: {missing[:12]}"
