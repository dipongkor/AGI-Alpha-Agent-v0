# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from scripts.ruff_targets import list_tracked_python_files


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def test_list_tracked_python_files_uses_git_index(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _git(repo, "init")
    _git(repo, "config", "user.email", "tests@example.com")
    _git(repo, "config", "user.name", "Test User")

    tracked = repo / "src" / "tracked_file.py"
    tracked.parent.mkdir(parents=True, exist_ok=True)
    tracked.write_text("x = 1\n", encoding="utf-8")

    _git(repo, "add", "src/tracked_file.py")
    _git(repo, "commit", "-m", "add tracked file")

    ref_file = repo / ".git" / "refs" / "remotes" / "origin" / "broken.py"
    ref_file.parent.mkdir(parents=True, exist_ok=True)
    ref_file.write_text("deadbeefdeadbeefdeadbeefdeadbeefdeadbeef\n", encoding="utf-8")

    targets = list_tracked_python_files(repo)

    assert "src/tracked_file.py" in targets
    assert all(not target.startswith(".git/") for target in targets)


def test_list_tracked_python_files_filters_metadata_paths(monkeypatch: Any, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    captured: dict[str, list[str]] = {}

    def fake_run(cmd: list[str], check: bool, capture_output: bool) -> SimpleNamespace:
        captured["cmd"] = cmd
        assert check is True
        assert capture_output is True
        payload = b"src/good.py\x00.cache/temp.py\x00nested/.git/bad.py\x00docs/readme.pyi\x00"
        return SimpleNamespace(stdout=payload)

    monkeypatch.setattr(subprocess, "run", fake_run)

    targets = list_tracked_python_files(repo)

    assert "--cached" in captured["cmd"]
    assert targets == ["docs/readme.pyi", "src/good.py"]
