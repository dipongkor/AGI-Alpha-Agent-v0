from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.select_insight_build_script import select_build_script


def test_select_build_script_uses_real_insight_package_contract() -> None:
    package_json = Path("alpha_factory_v1/demos/alpha_agi_insight_v1/insight_browser_v1/package.json")
    assert select_build_script(package_json) == "build:docs-insight"


def test_docs_build_alias_matches_primary_build_command() -> None:
    package_json = Path("alpha_factory_v1/demos/alpha_agi_insight_v1/insight_browser_v1/package.json")
    scripts = json.loads(package_json.read_text(encoding="utf-8"))["scripts"]
    assert scripts["build:docs-insight"] == scripts["build"]


def test_select_build_script_prefers_docs_alias_when_present(tmp_path: Path) -> None:
    package_json = tmp_path / "package.json"
    package_json.write_text(
        json.dumps(
            {
                "scripts": {
                    "build": "node build.js",
                    "build:insight": "node build-insight.js",
                    "build:docs-insight": "node build-docs.js",
                }
            }
        ),
        encoding="utf-8",
    )

    assert select_build_script(package_json) == "build:docs-insight"


def test_select_build_script_errors_when_missing(tmp_path: Path) -> None:
    package_json = tmp_path / "package.json"
    package_json.write_text(json.dumps({"scripts": {"lint": "eslint ."}}), encoding="utf-8")

    with pytest.raises(RuntimeError, match="No supported build script found"):
        select_build_script(package_json)
