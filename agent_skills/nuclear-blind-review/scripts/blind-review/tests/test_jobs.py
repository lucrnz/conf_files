from __future__ import annotations

import subprocess
from pathlib import Path

from blind_review.actions import jobs_payload


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def test_changes_mixed_two_plans(repo: Path) -> None:
    (repo / "src" / "app.py").write_text("print('changed')\n", encoding="utf-8")
    (repo / "docs" / "plans" / "001-alpha-pending" / "01.md").write_text(
        "# alpha edit\n", encoding="utf-8"
    )
    (repo / "docs" / "plans" / "002-beta-pending" / "01.md").write_text(
        "# beta edit\n", encoding="utf-8"
    )
    payload = jobs_payload(repo, "changes", None)
    jobs = payload["jobs"]
    assert [j["id"] for j in jobs] == [
        "code",
        "plan-001-alpha-pending",
        "plan-002-beta-pending",
    ]
    assert jobs[1]["plan_dir"] == "docs/plans/001-alpha-pending"
    assert jobs[2]["plan_dir"] == "docs/plans/002-beta-pending"


def test_changes_plan_only(repo: Path) -> None:
    (repo / "docs" / "plans" / "001-alpha-pending" / "01.md").write_text(
        "# only plan\n", encoding="utf-8"
    )
    jobs = jobs_payload(repo, "changes", None)["jobs"]
    assert [j["id"] for j in jobs] == ["plan-001-alpha-pending"]


def test_codebase_pending_only(repo: Path) -> None:
    jobs = jobs_payload(repo, "codebase", None)["jobs"]
    ids = [j["id"] for j in jobs]
    assert ids[0] == "code"
    assert "plan-001-alpha-pending" in ids
    assert "plan-002-beta-pending" in ids
    assert "plan-003-old-done" not in ids


def test_picker_range(repo: Path) -> None:
    _git(repo, "checkout", "-b", "work")
    (repo / "src" / "app.py").write_text("print('r')\n", encoding="utf-8")
    _git(repo, "add", "src/app.py")
    _git(repo, "commit", "-m", "code")
    (repo / "docs" / "plans" / "001-alpha-pending" / "01.md").write_text(
        "# ranged\n", encoding="utf-8"
    )
    _git(repo, "add", "docs/plans/001-alpha-pending/01.md")
    _git(repo, "commit", "-m", "plan")
    sha = __import__("subprocess").run(
        ["git", "-C", str(repo), "rev-parse", "HEAD~1"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    jobs = jobs_payload(repo, "picker", f"{sha}^..HEAD")["jobs"]
    assert [j["kind"] for j in jobs] == ["code", "plan"]
