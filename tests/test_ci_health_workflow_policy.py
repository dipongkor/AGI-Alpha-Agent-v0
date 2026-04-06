from __future__ import annotations

from pathlib import Path


def test_ci_health_workflow_run_is_rerun_only_and_context_aware() -> None:
    workflow = Path(".github/workflows/ci-health.yml").read_text(encoding="utf-8")

    assert 'workflows:\n      - "🚀 Integration CI — Insight Demo"\n      - "✅ PR CI"' in workflow
    assert 'HARD_WORKFLOW="pr-ci.yml"' in workflow
    assert 'if [[ "$source_workflow" == "🚀 Integration CI — Insight Demo" ]]; then' in workflow
    assert 'HARD_WORKFLOW="ci.yml"' in workflow
    assert "DISPATCH_ARGS=(--dispatch-missing)" in workflow
    assert "DISPATCH_ARGS=()" in workflow
    assert 'RERUN_ARGS+=("--rerun-failed")' in workflow


def test_ci_health_uses_required_checks_file_for_branch_protection_apply() -> None:
    workflow = Path(".github/workflows/ci-health.yml").read_text(encoding="utf-8")

    assert "python scripts/verify_branch_protection.py \\" in workflow
    assert "--required-checks-file scripts/required_checks.json" in workflow
