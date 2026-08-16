from __future__ import annotations

from pathlib import Path

from blind_review.actions import cleanup, prepare
from blind_review.select import PARENT_PREFIX


def test_prepare_creates_prefixed_parent(repo: Path) -> None:
    (repo / "src" / "app.py").write_text("print('x')\n", encoding="utf-8")
    out = prepare(
        repo,
        surface="changes",
        kind="code",
        plan_dir=None,
        parent=None,
        bars=[],
        git_range=None,
    )
    parent = Path(out["parent"])
    try:
        assert parent.name.startswith(PARENT_PREFIX)
        job = Path(out["job_dir"])
        assert (job / "src" / "app.py").is_file()
        assert (job / "README.md").is_file()
        assert (job / "AGENTS.md").is_file()
        assert not (job / "docs" / "plans").exists()
        assert not (job / "node_modules").exists()
        assert not (job / "debug.log").exists()
        assert not (job / ".env").exists()
        assert not (job / "big.bin").exists()
        assert not (job / ".git").exists()
        assert "docs/plans" not in (job / "DIFF.patch").read_text(encoding="utf-8")
        assert "app.py" in (job / "DIFF.patch").read_text(encoding="utf-8")
        listing = (job / "FILE_LIST.txt").read_text(encoding="utf-8")
        assert "src/app.py" in listing
        assert "docs/plans" not in listing
    finally:
        cleanup(parent)
        assert not parent.exists()


def test_prepare_plan_tree_has_code_and_plan_only_diff(
    repo: Path, tmp_path: Path
) -> None:
    bar = tmp_path / "plan-bar.md"
    bar.write_text("# plan bar\n", encoding="utf-8")
    (repo / "src" / "app.py").write_text("print('x')\n", encoding="utf-8")
    (repo / "docs" / "plans" / "001-alpha-pending" / "01.md").write_text(
        "# alpha edit\n", encoding="utf-8"
    )
    (repo / "docs" / "plans" / "002-beta-pending" / "01.md").write_text(
        "# beta edit\n", encoding="utf-8"
    )
    out = prepare(
        repo,
        surface="changes",
        kind="plan",
        plan_dir="docs/plans/001-alpha-pending",
        parent=None,
        bars=[bar],
        git_range=None,
    )
    parent = Path(out["parent"])
    try:
        job = Path(out["job_dir"])
        assert (job / "src" / "app.py").is_file()
        assert (job / "docs" / "plans" / "001-alpha-pending" / "01.md").is_file()
        assert not (job / "docs" / "plans" / "002-beta-pending").exists()
        assert not (job / "docs" / "plans" / "003-old-done").exists()
        diff = (job / "DIFF.patch").read_text(encoding="utf-8")
        assert "001-alpha-pending" in diff
        assert "src/app.py" not in diff
        assert (job / "_review" / "plan-bar.md").is_file()
    finally:
        cleanup(parent)


def test_codebase_prepare_omits_done_plans(repo: Path) -> None:
    out = prepare(
        repo,
        surface="codebase",
        kind="plan",
        plan_dir="docs/plans/001-alpha-pending",
        parent=None,
        bars=[],
        git_range=None,
    )
    parent = Path(out["parent"])
    try:
        job = Path(out["job_dir"])
        assert (job / "src" / "app.py").is_file()
        assert (job / "docs" / "plans" / "001-alpha-pending").is_dir()
        assert not (job / "docs" / "plans" / "003-old-done").exists()
        assert (job / "DIFF.patch").read_text(encoding="utf-8") == ""
    finally:
        cleanup(parent)
