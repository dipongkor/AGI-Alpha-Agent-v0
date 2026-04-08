from __future__ import annotations

from pathlib import Path


def test_repo_healer_workflow_installs_yaml_runtime_dependency() -> None:
    workflow = Path(".github/workflows/repo-healer.yml").read_text(encoding="utf-8")

    assert "name: Install Repo-Healer runtime dependencies" in workflow
    assert "python -m pip install pyyaml" in workflow
    assert "python -m alpha_factory_v1.demos.self_healing_repo.repo_healer_v1.ci_bundle" in workflow
