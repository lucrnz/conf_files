"""argparse CLI: discover script projects, clear caches, or uv sync."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_ERROR = 1

DISCOVERY_PRUNE = frozenset(
    {
        ".git",
        "node_modules",
        ".venv",
        ".cache",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".next",
        ".angular",
        ".turbo",
        ".parcel-cache",
        "dist",
        "build",
        "coverage",
        "htmlcov",
    }
)

ARTIFACT_DIRS = frozenset(
    {
        "node_modules",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "coverage",
        "htmlcov",
        ".next",
        ".vite",
        ".angular",
        ".turbo",
        ".parcel-cache",
        ".cache",
        "dist",
        "build",
    }
)

MARKER_NAMES = frozenset({"pyproject.toml", "package.json"})
COVERAGE_FILE = ".coverage"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="projects",
        description="Manage local script projects (clear caches or uv sync).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    clear = sub.add_parser("clear", help="Remove venvs and caches under --dir")
    clear.add_argument("--dir", default=".")
    clear.add_argument("-n", "--dry-run", action="store_true")

    sync = sub.add_parser("sync", help="Run uv sync on every uv project under --dir")
    sync.add_argument("--dir", default=".")

    args = parser.parse_args(argv)
    root = resolve_root(args.dir)
    if isinstance(root, int):
        return root
    if args.command == "clear":
        return run_clear(root, args.dry_run)
    return run_sync(root)


def resolve_root(raw: str) -> Path | int:
    root = Path(raw).expanduser()
    if not root.exists() or not root.is_dir():
        print(f"root directory not found: {root}", file=sys.stderr)
        return EXIT_ERROR
    return root.resolve()


def discover_projects(root: Path) -> list[Path]:
    found: set[Path] = set()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        dirnames[:] = [
            name
            for name in dirnames
            if name not in DISCOVERY_PRUNE and not (current / name).is_symlink()
        ]
        for name in filenames:
            if name not in MARKER_NAMES:
                continue
            path = current / name
            if path.is_symlink() or not path.is_file():
                continue
            found.add(current)
            break
    return sorted(found)


def list_artifacts(root: Path) -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        keep: list[str] = []
        for name in dirnames:
            child = current / name
            if child.is_symlink():
                continue
            if name == ".git":
                continue
            if name in ARTIFACT_DIRS:
                found.append(child)
                continue
            keep.append(name)
        dirnames[:] = keep
        for name in filenames:
            if name != COVERAGE_FILE:
                continue
            path = current / name
            if path.is_symlink() or not path.is_file():
                continue
            found.append(path)
    found.sort()
    return found


def print_discovered(root: Path, projects: list[Path]) -> None:
    print(f"Discovered projects under {root}:")
    for path in projects:
        print(f"  {path}")
    print()


def run_clear(root: Path, dry_run: bool) -> int:
    projects = discover_projects(root)
    if not projects:
        print(f"No script projects found under {root}")
        return EXIT_OK
    print_discovered(root, projects)
    if dry_run:
        print("Dry run: would remove:")
    else:
        print("Removing venvs and caches:")
    artifacts = list_artifacts(root)
    if not artifacts:
        print("  nothing to remove")
        return EXIT_OK
    for path in artifacts:
        print(f"  {path}")
        if dry_run:
            continue
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        except OSError as exc:
            print(f"failed to remove {path}: {exc}", file=sys.stderr)
            return EXIT_ERROR
    count = len(artifacts)
    if dry_run:
        print(f"Total: {count} item(s) (dry run, nothing deleted)")
    else:
        print(f"Removed {count} item(s)")
    return EXIT_OK


def _is_regular_file(path: Path) -> bool:
    return not path.is_symlink() and path.is_file()


def run_sync(root: Path) -> int:
    projects = discover_projects(root)
    if not projects:
        print(f"No script projects found under {root}")
        return EXIT_OK
    print_discovered(root, projects)
    if shutil.which("uv") is None:
        print("'uv' not found in PATH", file=sys.stderr)
        return EXIT_ERROR
    passed = 0
    failed: list[Path] = []
    skipped: list[Path] = []
    for directory in projects:
        pyproject = directory / "pyproject.toml"
        lock = directory / "uv.lock"
        if _is_regular_file(pyproject) and _is_regular_file(lock):
            print(f"==> uv sync: {directory}")
            result = subprocess.run(["uv", "sync"], cwd=directory)
            if result.returncode == 0:
                passed += 1
            else:
                failed.append(directory)
        else:
            skipped.append(directory)
    print()
    print(f"Summary: {passed} synced, {len(failed)} failed, {len(skipped)} skipped")
    if skipped:
        print("Skipped (not uv projects):")
        for path in skipped:
            print(f"  {path}")
    if failed:
        print("Failed:")
        for path in failed:
            print(f"  {path}")
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
