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
    assert 'apply_flag="--apply"' in workflow
    assert "ADMIN_GITHUB_TOKEN not set; running read-only branch protection check with default token." in workflow
    assert "--required-checks-file scripts/required_checks.json" in workflow
