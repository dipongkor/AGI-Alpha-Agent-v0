from __future__ import annotations

from pathlib import Path


def test_setup_node_cache_path_lifecycle_is_preserved() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert 'NPM_CONFIG_CACHE: ${{ github.workspace }}/.npm-cache/tests' in workflow
    assert "name: Ensure npm cache path lifecycle contract" in workflow
    assert "mkdir -p \"$NPM_CONFIG_CACHE\"" in workflow

    lines = workflow.splitlines()
    tests_job_idx = next(i for i, line in enumerate(lines) if 'name: "✅ Pytest (${{ matrix.python-version }})"' in line)
    ensure_idx = next(
        i for i, line in enumerate(lines) if i > tests_job_idx and "name: Ensure npm cache path lifecycle contract" in line
    )
    setup_node_idx = next(i for i, line in enumerate(lines) if i > tests_job_idx and "uses: actions/setup-node@" in line)
    cleanup_idx = next(i for i, line in enumerate(lines) if i > tests_job_idx and "rm -rf \"$NPM_CONFIG_CACHE\"" in line)
    recreate_idx = next(i for i, line in enumerate(lines) if i > cleanup_idx and "mkdir -p \"$NPM_CONFIG_CACHE\"" in line)

    assert tests_job_idx < ensure_idx < setup_node_idx
    assert cleanup_idx < recreate_idx
