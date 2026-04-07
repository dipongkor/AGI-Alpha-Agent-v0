# SPDX-License-Identifier: Apache-2.0
from pathlib import Path


def test_build_script_uses_src_scoped_removal_patterns() -> None:
    build_script = Path(
        "alpha_factory_v1/demos/alpha_agi_insight_v1/insight_browser_v1/build.js"
    ).read_text(encoding="utf-8")

    assert "/<script[^>]*\\bsrc=([\"'])[^\"']*bundle\\.esm\\.min\\.js" in build_script
    assert "/<script[^>]*\\bsrc=([\"'])[^\"']*pyodide\\.js" in build_script
    assert "<script[\\s\\S]*?bundle\\.esm\\.min\\.js[\\s\\S]*?</script>" not in build_script
    assert "<script[\\s\\S]*?pyodide\\.js[\\s\\S]*?</script>" not in build_script
