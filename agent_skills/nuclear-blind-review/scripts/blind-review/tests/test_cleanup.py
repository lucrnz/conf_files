from __future__ import annotations

from pathlib import Path

import pytest

from blind_review.actions import cleanup
from blind_review.gitops import GitError
from blind_review.select import PARENT_PREFIX


def test_cleanup_removes_prefixed_dir(tmp_path: Path) -> None:
    parent = tmp_path / f"{PARENT_PREFIX}xyz"
    parent.mkdir()
    (parent / "keep-marker").write_text("x", encoding="utf-8")
    cleanup(parent)
    assert not parent.exists()


def test_cleanup_refuses_other_names(tmp_path: Path) -> None:
    other = tmp_path / "not-ours"
    other.mkdir()
    marker = other / "stay"
    marker.write_text("x", encoding="utf-8")
    with pytest.raises(GitError, match="refusing to delete"):
        cleanup(other)
    assert marker.is_file()
