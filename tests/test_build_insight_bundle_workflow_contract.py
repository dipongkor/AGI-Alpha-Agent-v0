from __future__ import annotations

from pathlib import Path


def test_build_insight_bundle_workflow_uses_helper_script_detection() -> None:
    workflow = Path('.github/workflows/build-insight-bundle.yml').read_text(encoding='utf-8')

    assert 'scripts/select_insight_build_script.py' in workflow
    assert 'npm pkg get "scripts.' not in workflow


def test_build_insight_bundle_syncs_dist_to_docs_bundle() -> None:
    workflow = Path('.github/workflows/build-insight-bundle.yml').read_text(encoding='utf-8')

    assert '"${GITHUB_WORKSPACE}/${{ env.INSIGHT_BROWSER_DIR }}/dist/" "$GITHUB_WORKSPACE/${{ env.DOCS_BUNDLE_DIR }}/"' in workflow
    assert '--exclude=\'assets/wasm/**\'' in workflow
    assert '--exclude=\'assets/pyodide/**\'' in workflow
