"""Surface classification and include-set filters."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from blind_review.gitops import tracked_files

MAX_BYTES = 5 * 1024 * 1024
PLANS_ROOT = "docs/plans"
PARENT_PREFIX = "nuclear-blind-"

JUNK_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "logs",
    "node_modules",
    "target",
    "vendor",
    "venv",
}

BINARY_SUFFIXES = {
    ".dylib",
    ".exe",
    ".gif",
    ".gz",
    ".jpeg",
    ".jpg",
    ".o",
    ".pdf",
    ".png",
    ".pyc",
    ".so",
    ".webp",
    ".woff",
    ".woff2",
    ".zip",
}

SKIP_SUFFIXES = {
    ".db",
    ".key",
    ".log",
    ".p12",
    ".pem",
    ".sqlite",
    ".sqlite3",
} | BINARY_SUFFIXES

SECRET_NAMES = {
    ".env",
    "credentials.json",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
}


def posix(rel: str) -> str:
    return str(PurePosixPath(*Path(rel).parts))


def plan_dir_of(rel: str) -> str | None:
    parts = PurePosixPath(posix(rel)).parts
    if len(parts) >= 3 and parts[0] == "docs" and parts[1] == "plans":
        return f"{parts[0]}/{parts[1]}/{parts[2]}"
    return None


def under_plans(rel: str) -> bool:
    p = posix(rel)
    return p == PLANS_ROOT or p.startswith(PLANS_ROOT + "/")


def classify_jobs(surface_paths: list[str]) -> list[dict]:
    plan_dirs: set[str] = set()
    has_code = False
    for rel in surface_paths:
        pd = plan_dir_of(rel)
        if pd is not None:
            plan_dirs.add(pd)
        elif under_plans(rel):
            continue
        else:
            has_code = True
    jobs: list[dict] = []
    if has_code:
        jobs.append({"id": "code", "kind": "code"})
    for pd in sorted(plan_dirs):
        name = PurePosixPath(pd).name
        jobs.append({"id": f"plan-{name}", "kind": "plan", "plan_dir": pd})
    return jobs


def pending_plan_dirs(repo: Path) -> list[str]:
    root = repo / "docs" / "plans"
    if not root.is_dir():
        return []
    found: list[str] = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and child.name.endswith("-pending"):
            found.append(posix(str(Path("docs") / "plans" / child.name)))
    return found


def is_secret_name(name: str) -> bool:
    if name in SECRET_NAMES or name.startswith(".env"):
        return True
    suffix = Path(name).suffix.lower()
    return suffix in SKIP_SUFFIXES


def has_junk_dir(rel: str) -> bool:
    return any(part in JUNK_DIRS for part in PurePosixPath(posix(rel)).parts)


def looks_binary(path: Path) -> bool:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return True
    try:
        with path.open("rb") as fh:
            chunk = fh.read(8192)
    except OSError:
        return False
    return b"\0" in chunk


def skip_file(repo: Path, rel: str) -> bool:
    if has_junk_dir(rel):
        return True
    if is_secret_name(Path(rel).name):
        return True
    src = repo / rel
    if not src.is_file():
        return True
    try:
        if src.stat().st_size > MAX_BYTES:
            return True
    except OSError:
        return True
    return looks_binary(src)


def include_set(
    repo: Path,
    *,
    kind: str,
    plan_dir: str | None,
    extras: list[str],
) -> list[str]:
    """Tracked files plus extras (untracked), filtered for a job."""
    candidates = set(tracked_files(repo))
    candidates.update(extras)
    kept: list[str] = []
    for rel in sorted(candidates):
        rel = posix(rel)
        if skip_file(repo, rel):
            continue
        pd = plan_dir_of(rel)
        if kind == "code":
            if under_plans(rel):
                continue
        elif kind == "plan":
            if under_plans(rel) and (plan_dir is None or pd != plan_dir):
                continue
        kept.append(rel)
    return kept
