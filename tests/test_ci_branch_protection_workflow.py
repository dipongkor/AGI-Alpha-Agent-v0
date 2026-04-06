from __future__ import annotations

from pathlib import Path


def test_branch_protection_job_uses_admin_token_only_for_apply() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert 'name: "🔒 Branch protection guardrails"' in workflow
    assert "ADMIN_GITHUB_TOKEN: ${{ secrets.ADMIN_GITHUB_TOKEN }}" in workflow
    assert (
        "GITHUB_TOKEN: ${{ secrets.ADMIN_GITHUB_TOKEN != '' && secrets.ADMIN_GITHUB_TOKEN || github.token }}"
        in workflow
    )

    guard_line = 'if [ -n "${ADMIN_GITHUB_TOKEN}" ]; then'
    apply_line = 'apply_flag="--apply"'
    notice_line = "ADMIN_GITHUB_TOKEN not set; running read-only branch protection check with default token."
    verify_line = "python scripts/verify_branch_protection.py"

    assert guard_line in workflow
    assert apply_line in workflow
    assert notice_line in workflow
    assert verify_line in workflow
    assert '--branch "${TARGET_BRANCH}"' in workflow
    assert "${apply_flag}" in workflow
    assert "--required-checks-file scripts/required_checks.json" in workflow

    guard_pos = workflow.index(guard_line)
    apply_pos = workflow.index(apply_line, guard_pos)
    verify_pos = workflow.index(verify_line, apply_pos)
    apply_flag_use_pos = workflow.index("${apply_flag}", verify_pos)

    assert guard_pos < apply_pos < verify_pos < apply_flag_use_pos
