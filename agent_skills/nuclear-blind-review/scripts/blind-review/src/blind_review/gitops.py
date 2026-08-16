"""Git helpers. Fail clearly if git is missing or the path is not a repo."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


def require_git() -> str:
    exe = shutil.which("git")
    if exe is None:
        raise GitError("git is required but was not found on PATH")
    return exe


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    exe = require_git()
    result = subprocess.run(
        [exe, "-C", str(repo), *args],
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        err = (result.stderr or result.stdout or "git failed").strip()
        raise GitError(err)
    return result


def assert_repo(repo: Path) -> None:
    result = git(repo, "rev-parse", "--is-inside-work-tree", check=False)
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise GitError(f"not a git repository: {repo}")


def tracked_files(repo: Path) -> list[str]:
    out = git(repo, "ls-files", "-z").stdout
    return [p for p in out.split("\0") if p]


def untracked_not_ignored(repo: Path) -> list[str]:
    out = git(repo, "ls-files", "-z", "--others", "--exclude-standard").stdout
    return [p for p in out.split("\0") if p]


def changes_surface(repo: Path) -> list[str]:
    """Staged ∪ unstaged ∪ untracked (not ignored). Includes deleted paths."""
    names: set[str] = set()
    for args in (
        ("diff", "--name-only", "-z"),
        ("diff", "--cached", "--name-only", "-z"),
        ("ls-files", "-z", "--others", "--exclude-standard"),
    ):
        out = git(repo, *args).stdout
        names.update(p for p in out.split("\0") if p)
    return sorted(names)


def range_surface(repo: Path, git_range: str) -> list[str]:
    out = git(repo, "diff", "--name-only", "-z", git_range).stdout
    return [p for p in out.split("\0") if p]


def unified_diff(repo: Path, *pathspecs: str, git_range: str | None = None) -> str:
    """Working tree vs HEAD, or a picker range. pathspecs are git pathspecs."""
    if git_range:
        args = ["diff", "--binary", git_range]
    else:
        args = ["diff", "--binary", "HEAD"]
    if pathspecs:
        args += ["--", *pathspecs]
    return git(repo, *args, check=False).stdout


def untracked_as_diff(repo: Path, rel: str) -> str:
    src = repo / rel
    if not src.is_file():
        return ""
    result = git(repo, "diff", "--no-index", "--binary", "/dev/null", rel, check=False)
    # git --no-index exits 1 when files differ
    return result.stdout
