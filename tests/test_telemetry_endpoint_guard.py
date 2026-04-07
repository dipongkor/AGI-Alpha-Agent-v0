# SPDX-License-Identifier: Apache-2.0
from pathlib import Path


def test_telemetry_guards_import_meta_env() -> None:
    source = Path("alpha_factory_v1/core/telemetry.js").read_text(encoding="utf-8")
    assert "import.meta.env ? import.meta.env.VITE_OTEL_ENDPOINT : undefined" in source
