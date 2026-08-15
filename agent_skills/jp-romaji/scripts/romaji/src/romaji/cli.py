"""argparse CLI: Japanese lines in, JSONL engine votes out."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from romaji import cutlet_engine, pykakasi_engine

ENGINES = ("pykakasi", "cutlet", "both")


def _read_lines(files: list[str]) -> list[str]:
    if not files:
        raw = sys.stdin.read()
        parts = raw.splitlines()
    else:
        parts = []
        for name in files:
            text = Path(name).read_text(encoding="utf-8")
            parts.extend(text.splitlines())
    return [line for line in parts if line.strip() != ""]


def _record(line: str, engine: str) -> dict:
    rec: dict = {"orig": line}
    if engine in ("pykakasi", "both"):
        rec["pykakasi"] = pykakasi_engine.convert(line)
    if engine in ("cutlet", "both"):
        rec["cutlet"] = cutlet_engine.convert(line)
    return rec


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="romaji",
        description="Emit pykakasi and/or cutlet readings as JSONL.",
    )
    parser.add_argument(
        "--engine",
        choices=ENGINES,
        default="both",
        help="which converter(s) to run (default: both)",
    )
    parser.add_argument("files", nargs="*", metavar="FILE")
    args = parser.parse_args(argv)
    try:
        for line in _read_lines(args.files):
            print(json.dumps(_record(line, args.engine), ensure_ascii=False))
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
