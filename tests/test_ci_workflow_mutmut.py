from __future__ import annotations

from pathlib import Path


def test_ci_mutmut_step_is_config_driven() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "mutmut --version" in workflow
    assert 'PYTEST_ADDOPTS="tests/test_mutation_smoke_target.py -q" timeout 20m mutmut run' in workflow
    assert "[tool.mutmut] must be configured in pyproject.toml" in workflow
    assert "[tool.mutmut].paths_to_mutate must be configured" in workflow
    assert "[tool.mutmut].pytest_add_cli_args_test_selection must be configured" in workflow
    assert "args+=(--paths-to-mutate" not in workflow
    assert "args+=(--runner" not in workflow
    assert "mutmut run --paths-to-mutate" not in workflow
    assert "mutmut run --runner" not in workflow


def test_mutmut_paths_configured_in_pyproject() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.mutmut]" in pyproject
    assert "scripts/mutation_smoke_target.py" in pyproject
    assert "pytest_add_cli_args_test_selection" in pyproject
    assert "mutate_only_covered_lines = true" in pyproject


def test_mutmut_version_is_pinned_in_dev_lockfile() -> None:
    lock = Path("requirements-dev.lock").read_text(encoding="utf-8")
    assert "mutmut==3.3.0 \\" in lock
