# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from types import SimpleNamespace

from scripts.verify_demo_pages import (
    DEMO_READINESS_SELECTORS,
    DEMO_REQUIRED_LOCAL_ASSETS,
    DOCS_DIR,
    _build_demo_url,
    _extract_failure_text,
    _insight_contract_ok,
    _is_ignorable_insight_page_error,
    _is_ready,
    _missing_required_assets,
)


def test_extract_failure_text_with_none() -> None:
    assert _extract_failure_text(None) == "unknown"


def test_extract_failure_text_with_string() -> None:
    assert _extract_failure_text("net::ERR_FAILED") == "net::ERR_FAILED"


def test_extract_failure_text_with_dict() -> None:
    assert _extract_failure_text({"errorText": "timeout"}) == "timeout"


def test_extract_failure_text_with_object_attribute() -> None:
    failure = SimpleNamespace(error_text="connection reset")
    assert _extract_failure_text(failure) == "connection reset"


def test_extract_failure_text_with_object_camel_case_attribute() -> None:
    failure = SimpleNamespace(errorText="request aborted")
    assert _extract_failure_text(failure) == "request aborted"


def test_extract_failure_text_with_callable() -> None:
    assert _extract_failure_text(lambda: "broken pipe") == "broken pipe"


def test_extract_failure_text_with_callable_exception() -> None:
    def _boom() -> str:
        raise RuntimeError("nope")

    assert _extract_failure_text(_boom) == "unknown"


def test_build_demo_url_uses_http() -> None:
    demo = DOCS_DIR / "alpha_agi_insight_v1"
    url = _build_demo_url("http://127.0.0.1:9999", demo)

    assert url.startswith("http://127.0.0.1:9999/")
    assert url.endswith("/alpha_agi_insight_v1/index.html")
    assert not url.startswith("file://")


def test_insight_page_uses_explicit_readiness_contract() -> None:
    assert DEMO_READINESS_SELECTORS["alpha_agi_insight_v1"] == ("html[data-insight-ready='1']", "#root")
    assert DEMO_REQUIRED_LOCAL_ASSETS["alpha_agi_insight_v1"] == (
        "insight.bundle.js",
        "style.css",
        "assets/d3.v7.min.js",
        "assets/src/i18n/en.json",
    )


def test_is_ready_requires_insight_marker_or_mounted_root() -> None:
    demo = DOCS_DIR / "alpha_agi_insight_v1"
    assert _is_ready(demo, {"match": "main h1", "hasMain": True, "bodyTextLen": 200}) == (False, "")
    assert _is_ready(demo, {"match": "#root", "rootChildCount": 0}) == (False, "")
    assert _is_ready(demo, {"match": "#root", "rootChildCount": 1}) == (True, "insight-root-mounted")


def test_insight_contract_requires_clean_runtime() -> None:
    assert _insight_contract_ok([], [], [], []) == (True, "")
    assert _insight_contract_ok([], [], [], ["src/i18n/en.json"]) == (False, "missing-required-assets")
    assert _insight_contract_ok([], ["missing.js"], [], []) == (False, "missing-local-assets")
    assert _insight_contract_ok([], [], ["x -> 404"], []) == (False, "http-error-responses")
    assert _insight_contract_ok(["TypeError"], [], [], []) == (False, "page-errors")
    assert _insight_contract_ok(
        ["Failed to execute 'postMessage': The target origin provided does not match the recipient window's origin"],
        [],
        [],
        [],
    ) == (False, "page-errors")


def test_is_ignorable_insight_page_error_is_limited_to_known_sandbox_messages() -> None:
    assert _is_ignorable_insight_page_error("Service worker is disabled because the context is sandboxed")
    assert not _is_ignorable_insight_page_error("Cannot read properties of undefined (reading 'NaN')")
    assert _is_ignorable_insight_page_error(
        "Cannot read properties of undefined (reading 'NaN')\n"
        "TypeError: Cannot read properties of undefined (reading 'NaN')\n"
        "    at V$ (http://127.0.0.1/demo/insight.bundle.js:2907:1431)"
    )


def test_missing_required_assets_detects_insight_contract_files(tmp_path) -> None:
    demo_dir = tmp_path / "alpha_agi_insight_v1"
    (demo_dir / "src" / "i18n").mkdir(parents=True)
    (demo_dir / "insight.bundle.js").write_text("", encoding="utf-8")
    (demo_dir / "style.css").write_text("", encoding="utf-8")
    (demo_dir / "assets").mkdir(parents=True, exist_ok=True)
    (demo_dir / "assets" / "d3.v7.min.js").write_text("", encoding="utf-8")
    (demo_dir / "assets" / "src" / "i18n").mkdir(parents=True, exist_ok=True)
    (demo_dir / "assets" / "src" / "i18n" / "en.json").write_text("{}", encoding="utf-8")
    assert _missing_required_assets(demo_dir) == []

    (demo_dir / "assets" / "src" / "i18n" / "en.json").unlink(missing_ok=True)
    assert _missing_required_assets(demo_dir) == ["assets/src/i18n/en.json"]
