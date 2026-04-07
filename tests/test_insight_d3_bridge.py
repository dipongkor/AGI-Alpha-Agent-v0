# SPDX-License-Identifier: Apache-2.0
from pathlib import Path


def test_d3_bridge_imports_local_asset_path() -> None:
    bridge = Path("alpha_factory_v1/demos/alpha_agi_insight_v1/insight_browser_v1/d3.exports.js")
    text = bridge.read_text(encoding="utf-8")
    assert 'import "./assets/d3.v7.min.js";' in text
