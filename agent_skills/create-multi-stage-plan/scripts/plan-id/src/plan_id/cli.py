"""argparse CLI: mint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from plan_id.names import MintError, mint


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="plan-id")
    sub = parser.add_subparsers(dest="cmd", required=True)
    mint_p = sub.add_parser("mint", help="print one unused plan directory basename")
    mint_p.add_argument("--plans-dir", required=True, type=Path)
    mint_p.add_argument("--slug", required=True)
    mint_p.add_argument("--date", default=None)
    args = parser.parse_args(argv)
    try:
        print(mint(args.plans_dir, args.slug, args.date))
    except MintError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
