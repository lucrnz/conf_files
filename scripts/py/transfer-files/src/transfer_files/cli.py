"""argparse CLI: copy files matching extensions into a destination."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_ERROR = 1
CHUNK = 1024 * 1024


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="transfer-files",
        description="Copy files matching extensions into a destination.",
    )
    parser.add_argument("--ext", "-e", action="append", required=True)
    parser.add_argument("--dest", "-d", required=True)
    parser.add_argument("--verify", "-V", action="store_true")
    args = parser.parse_args(argv)
    exts = parse_exts(args.ext)
    if not exts:
        print("at least one non-empty extension is required", file=sys.stderr)
        return EXIT_USAGE
    return run(exts, Path(args.dest), args.verify)


def parse_exts(values: list[str]) -> set[str]:
    out: set[str] = set()
    for raw in values:
        for part in raw.split(","):
            token = part.strip()
            if token.startswith("."):
                token = token[1:]
            token = token.lower()
            if token:
                out.add(token)
    return out


def run(exts: set[str], dest: Path, verify: bool) -> int:
    dest = dest.expanduser()
    if not dest.exists() or not dest.is_dir():
        print(f"destination is not a directory: {dest}", file=sys.stderr)
        return EXIT_ERROR
    dest = dest.resolve()
    cwd = Path.cwd().resolve()
    skip_under = dest if _is_under(dest, cwd) else None

    for dirpath, dirnames, filenames in os.walk(cwd, followlinks=False):
        current = Path(dirpath)
        dirnames[:] = [name for name in dirnames if not (current / name).is_symlink()]
        if skip_under is not None:
            dirnames[:] = [
                name
                for name in dirnames
                if not _is_under((current / name).resolve(), skip_under)
            ]
        for name in filenames:
            source = current / name
            if source.is_symlink() or not source.is_file():
                continue
            if skip_under is not None and _is_under(source.resolve(), skip_under):
                continue
            suffix = source.suffix[1:].lower() if source.suffix else ""
            if suffix not in exts:
                continue
            rel = source.relative_to(cwd)
            dest_file = dest / rel
            code = copy_one(source, dest_file, rel, verify)
            if code != EXIT_OK:
                return code
    return EXIT_OK


def copy_one(source: Path, dest_file: Path, rel: Path, verify: bool) -> int:
    if dest_file.exists():
        return EXIT_OK
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(source, dest_file)
    except OSError as exc:
        print(f"copy failed: {rel}: {exc}", file=sys.stderr)
        return EXIT_ERROR
    print(f">Copying {rel}")
    if not verify:
        return EXIT_OK
    if sha256_file(source) == sha256_file(dest_file):
        return EXIT_OK
    dest_file.unlink(missing_ok=True)
    print(f"sha256 mismatch after copy: {rel}", file=sys.stderr)
    return EXIT_ERROR


def sha256_file(path: Path) -> bytes:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(CHUNK)
            if not chunk:
                break
            digest.update(chunk)
    return digest.digest()


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
