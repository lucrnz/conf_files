"""argparse CLI: recompress zip archives with 7z."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_ERROR = 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rearchiver",
        description="Recompress zip archives with 7z.",
    )
    parser.add_argument("--target", "-t", required=True)
    parser.add_argument("--level", "-l", type=int, default=9)
    args = parser.parse_args(argv)
    if args.level not in range(10):
        print("level must be an integer from 0 to 9", file=sys.stderr)
        return EXIT_USAGE
    return run(Path(args.target), args.level)


def run(target: Path, level: int) -> int:
    target = target.expanduser()
    if not target.exists():
        print(f"target does not exist: {target}", file=sys.stderr)
        return EXIT_ERROR
    target = target.resolve()
    if target.is_file():
        if target.suffix.lower() != ".zip":
            print(f"not a zip file: {target}", file=sys.stderr)
            return EXIT_ERROR
        zips = [target]
    elif target.is_dir():
        zips = list_zips(target)
    else:
        print(f"target is not a file or directory: {target}", file=sys.stderr)
        return EXIT_ERROR

    if not zips:
        return EXIT_OK

    seven_z = shutil.which("7z")
    if seven_z is None:
        print("7z not found on PATH", file=sys.stderr)
        return EXIT_ERROR

    for archive in zips:
        code = recompress(archive, level, seven_z)
        if code != EXIT_OK:
            return code
    return EXIT_OK


def list_zips(root: Path) -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        dirnames[:] = [name for name in dirnames if not (current / name).is_symlink()]
        for name in filenames:
            path = current / name
            if path.is_symlink() or not path.is_file():
                continue
            if path.suffix.lower() == ".zip":
                found.append(path)
    found.sort()
    return found


def recompress(archive: Path, level: int, seven_z: str) -> int:
    print(f"Processing {archive}")
    with (
        tempfile.TemporaryDirectory() as extract_dir,
        tempfile.TemporaryDirectory() as out_dir,
    ):
        tmp_zip = Path(out_dir) / "out.zip"
        extracted = _run_7z([seven_z, "x", str(archive)], cwd=extract_dir)
        if extracted != EXIT_OK:
            return extracted
        written = _run_7z(
            [seven_z, "a", "-tzip", f"-mx{level}", str(tmp_zip), "."],
            cwd=extract_dir,
        )
        if written != EXIT_OK:
            return written
        shutil.move(str(tmp_zip), str(archive))
    return EXIT_OK


def _run_7z(argv: list[str], cwd: str) -> int:
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    if result.returncode == 0:
        return EXIT_OK
    text = result.stderr if result.stderr else result.stdout
    if text:
        sys.stderr.write(text)
        if not text.endswith("\n"):
            sys.stderr.write("\n")
    else:
        print(f"7z failed: {' '.join(argv)}", file=sys.stderr)
    return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
