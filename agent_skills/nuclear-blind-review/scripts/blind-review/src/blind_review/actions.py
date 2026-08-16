"""jobs / prepare / cleanup."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from blind_review import gitops
from blind_review.select import (
    PARENT_PREFIX,
    classify_jobs,
    include_set,
    pending_plan_dirs,
    posix,
    skip_file,
    under_plans,
)


def jobs_payload(repo: Path, surface: str, git_range: str | None) -> dict:
    gitops.assert_repo(repo)
    if surface == "changes":
        paths = gitops.changes_surface(repo)
        job_list = classify_jobs(paths)
    elif surface == "picker":
        if not git_range:
            raise gitops.GitError("picker surface requires --range")
        paths = gitops.range_surface(repo, git_range)
        job_list = classify_jobs(paths)
    elif surface == "codebase":
        tracked = gitops.tracked_files(repo)
        code_paths = [p for p in tracked if not under_plans(p)]
        job_list = classify_jobs(code_paths)
        for pd in pending_plan_dirs(repo):
            name = Path(pd).name
            job_list.append({"id": f"plan-{name}", "kind": "plan", "plan_dir": pd})
    else:
        raise gitops.GitError(f"unknown surface: {surface}")
    return {"jobs": job_list}


def _job_id(kind: str, plan_dir: str | None) -> str:
    if kind == "code":
        return "code"
    if not plan_dir:
        raise gitops.GitError("plan job requires --plan-dir")
    return f"plan-{Path(plan_dir).name}"


def _copy_tree(repo: Path, dest: Path, rels: list[str]) -> None:
    for rel in rels:
        src = repo / rel
        if not src.is_file():
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)


def _write_diff(
    repo: Path,
    dest: Path,
    *,
    kind: str,
    plan_dir: str | None,
    surface: str,
    git_range: str | None,
    extras: list[str],
) -> None:
    if surface == "codebase":
        dest.write_text("", encoding="utf-8")
        return
    range_arg = git_range if surface == "picker" else None
    if kind == "code":
        text = gitops.unified_diff(repo, ".", ":!docs/plans", git_range=range_arg)
        if surface == "changes":
            for rel in extras:
                if under_plans(rel) or skip_file(repo, rel):
                    continue
                text += gitops.untracked_as_diff(repo, rel)
    else:
        if not plan_dir:
            raise gitops.GitError("plan job requires --plan-dir")
        text = gitops.unified_diff(repo, plan_dir, git_range=range_arg)
        if surface == "changes":
            for rel in extras:
                if posix(rel) == plan_dir or posix(rel).startswith(plan_dir + "/"):
                    if skip_file(repo, rel):
                        continue
                    text += gitops.untracked_as_diff(repo, rel)
    dest.write_text(text, encoding="utf-8")


def prepare(
    repo: Path,
    *,
    surface: str,
    kind: str,
    plan_dir: str | None,
    parent: Path | None,
    bars: list[Path],
    git_range: str | None,
) -> dict:
    gitops.assert_repo(repo)
    if kind not in {"code", "plan"}:
        raise gitops.GitError(f"unknown kind: {kind}")
    if kind == "plan" and not plan_dir:
        raise gitops.GitError("plan job requires --plan-dir")
    if surface == "picker" and not git_range:
        raise gitops.GitError("picker surface requires --range")

    created = False
    if parent is None:
        parent = Path(tempfile.mkdtemp(prefix=PARENT_PREFIX))
        created = True
    else:
        parent.mkdir(parents=True, exist_ok=True)

    job_id = _job_id(kind, plan_dir)
    job_dir = parent / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir)
    job_dir.mkdir(parents=True)

    extras: list[str] = []
    if surface == "changes":
        extras = gitops.untracked_not_ignored(repo)

    rels = include_set(repo, kind=kind, plan_dir=plan_dir, extras=extras)
    _copy_tree(repo, job_dir, rels)
    (job_dir / "FILE_LIST.txt").write_text(
        "".join(f"{r}\n" for r in rels), encoding="utf-8"
    )
    _write_diff(
        repo,
        job_dir / "DIFF.patch",
        kind=kind,
        plan_dir=plan_dir,
        surface=surface,
        git_range=git_range,
        extras=extras,
    )
    review_dir = job_dir / "_review"
    review_dir.mkdir()
    for bar in bars:
        src = Path(bar)
        if not src.is_file():
            if created:
                shutil.rmtree(parent, ignore_errors=True)
            raise gitops.GitError(f"bar file not found: {src}")
        shutil.copy2(src, review_dir / src.name)

    job: dict = {"id": job_id, "kind": kind}
    if plan_dir:
        job["plan_dir"] = posix(plan_dir)
    return {"parent": str(parent), "job_dir": str(job_dir), "job": job}


def cleanup(parent: Path) -> None:
    path = parent.expanduser()
    try:
        path = path.resolve()
    except OSError as exc:
        raise gitops.GitError(f"cannot resolve parent: {exc}") from exc
    if not path.name.startswith(PARENT_PREFIX):
        raise gitops.GitError(
            f"refusing to delete {path}: basename must start with {PARENT_PREFIX!r}"
        )
    if not path.is_dir():
        raise gitops.GitError(f"not a directory: {path}")
    shutil.rmtree(path)


def dumps(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)
