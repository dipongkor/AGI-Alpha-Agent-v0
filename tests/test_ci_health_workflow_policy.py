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


def test_ci_health_uses_apply_on_verify_branch_protection_call() -> None:
    workflow = Path(".github/workflows/ci-health.yml").read_text(encoding="utf-8")
    lines = workflow.splitlines()

    verify_idx = next(i for i, line in enumerate(lines) if "python scripts/verify_branch_protection.py" in line)
    call_window = "\n".join(lines[slice(verify_idx, verify_idx + 6)])

    assert '--branch "${CI_POLICY_BRANCH}"' in call_window
    assert "--apply" in call_window
    assert "--required-checks-file scripts/required_checks.json" in call_window
