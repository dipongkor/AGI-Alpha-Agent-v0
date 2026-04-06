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
    assert "python scripts/verify_branch_protection.py" in workflow
    assert '--branch "${TARGET_BRANCH}"' in workflow
    assert "${apply_flag}" in workflow
    assert "--required-checks-file scripts/required_checks.json" in workflow

    lines = workflow.splitlines()
    guard_idx = next(i for i, line in enumerate(lines) if 'if [ -n "${ADMIN_GITHUB_TOKEN}" ]; then' in line)
    else_idx = next(i for i, line in enumerate(lines[guard_idx + 1 :], start=guard_idx + 1) if line.strip() == "else")
    fi_idx = next(i for i, line in enumerate(lines[else_idx + 1 :], start=else_idx + 1) if line.strip() == "fi")

    then_block = "\n".join(lines[guard_idx + 1 : else_idx])
    else_block = "\n".join(lines[else_idx + 1 : fi_idx])
    post_guard_block = "\n".join(lines[fi_idx + 1 :])

    assert 'apply_flag="--apply"' in then_block
    assert 'apply_flag="--apply"' not in else_block
    assert 'apply_flag="--apply"' not in post_guard_block
    assert "ADMIN_GITHUB_TOKEN not set; running read-only branch protection check with default token." in else_block

    verify_idx = next(i for i, line in enumerate(lines[fi_idx + 1 :], start=fi_idx + 1) if "python scripts/verify_branch_protection.py" in line)
    apply_flag_use_idx = next(i for i, line in enumerate(lines[verify_idx + 1 :], start=verify_idx + 1) if "${apply_flag}" in line)

    assert guard_idx < else_idx < fi_idx < verify_idx < apply_flag_use_idx
