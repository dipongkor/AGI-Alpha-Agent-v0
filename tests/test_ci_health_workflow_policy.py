from __future__ import annotations

from pathlib import Path


def test_ci_health_workflow_run_is_rerun_only_and_context_aware() -> None:
    workflow = Path(".github/workflows/ci-health.yml").read_text(encoding="utf-8")

    assert 'workflows:\n      - "🚀 Integration CI — Insight Demo"\n      - "✅ PR CI"' in workflow
    assert 'HARD_WORKFLOW="pr-ci.yml"' in workflow

    workflow_run_block = """
          if [[ "${{ github.event_name }}" == "workflow_run" ]]; then
            source_workflow=$(jq -r '.workflow_run.name // empty' "$GITHUB_EVENT_PATH")
            if [[ "$source_workflow" == "🚀 Integration CI — Insight Demo" ]]; then
              HARD_WORKFLOW="ci.yml"
            fi
            # A completed workflow_run already guarantees a concrete run exists.
            # Avoid extra dispatches in this context and only rerun failed runs.
            DISPATCH_ARGS=()
            # Repo-Healer marks run_attempt<2 as report-only; keep one automatic rerun
            # path for failed workflow_run contexts so AUTOPATCH_SAFE can activate.
            RERUN_ARGS+=("--rerun-failed")
          fi
    """.strip()
    assert workflow_run_block in workflow
    assert "DISPATCH_ARGS=(--dispatch-missing)" in workflow


def test_ci_health_uses_required_checks_file_for_branch_protection_apply() -> None:
    workflow = Path(".github/workflows/ci-health.yml").read_text(encoding="utf-8")

    assert "python scripts/verify_branch_protection.py \\" in workflow
    assert "--required-checks-file scripts/required_checks.json" in workflow
