from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from blind_review.select import MAX_BYTES


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Test")

    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")
    (root / "README.md").write_text("# app\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("use python\n", encoding="utf-8")

    for name in ("001-alpha-pending", "002-beta-pending", "003-old-done"):
        d = root / "docs" / "plans" / name
        d.mkdir(parents=True)
        (d / "01.md").write_text(f"# {name}\n", encoding="utf-8")

    (root / ".gitignore").write_text("node_modules/\n*.log\n.env\n", encoding="utf-8")
    (root / "node_modules" / "pkg").mkdir(parents=True)
    (root / "node_modules" / "pkg" / "x.js").write_text("x\n", encoding="utf-8")
    (root / "debug.log").write_text("log\n", encoding="utf-8")
    (root / ".env").write_text("SECRET=1\n", encoding="utf-8")
    (root / "big.bin").write_bytes(b"\0" * (MAX_BYTES + 1))

    git(root, "add", "-A")
    git(root, "commit", "-m", "init")
    return root
