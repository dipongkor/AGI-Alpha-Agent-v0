# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pathlib import Path

from scripts.verify_gallery_assets import collect_missing_preview_assets


def _write_demo_page(path: Path, preview_ref: str) -> None:
    path.write_text(
        "\n".join(
            [
                "[See docs/DISCLAIMER_SNIPPET.md](../DISCLAIMER_SNIPPET.md)",
                "",
                "# Demo",
                "",
                f"![preview]({preview_ref}){{.demo-preview}}",
            ]
        ),
        encoding="utf-8",
    )


def test_collect_missing_preview_assets_reports_missing_file(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "docs" / "demos").mkdir(parents=True)
    _write_demo_page(repo / "docs" / "demos" / "demo_a.md", "../demo_a/assets/preview.svg")

    missing = collect_missing_preview_assets(repo)
    assert missing == ["docs/demos/demo_a.md: docs/demo_a/assets/preview.svg"]


def test_collect_missing_preview_assets_passes_with_existing_preview(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "docs" / "demos").mkdir(parents=True)
    (repo / "docs" / "demo_a" / "assets").mkdir(parents=True)
    (repo / "docs" / "demo_a" / "assets" / "preview.svg").write_text("<svg/>", encoding="utf-8")
    _write_demo_page(repo / "docs" / "demos" / "demo_a.md", "../demo_a/assets/preview.svg")

    assert collect_missing_preview_assets(repo) == []


def test_repo_contract_includes_insight_preview_asset() -> None:
    repo = Path(__file__).resolve().parents[1]
    missing = collect_missing_preview_assets(repo)
    assert missing == []
    preview = repo / "docs" / "alpha_agi_insight_v1" / "assets" / "preview.svg"
    source = repo / "docs" / "alpha_factory_v1" / "demos" / "alpha_agi_insight_v1" / "assets" / "preview.svg"

    assert preview.is_file()
    assert source.is_file()
    assert preview.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")
