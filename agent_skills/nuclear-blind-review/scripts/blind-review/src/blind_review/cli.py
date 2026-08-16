"""argparse CLI: jobs, prepare, cleanup."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from blind_review import actions
from blind_review.gitops import GitError


def _repo(value: str) -> Path:
    return Path(value).expanduser().resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="blind-review",
        description="Classify review surfaces and build isolated review packages.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    jobs_p = sub.add_parser("jobs", help="print mechanical job list")
    jobs_p.add_argument("--repo", required=True, type=_repo)
    jobs_p.add_argument("--surface", required=True, choices=("changes", "codebase", "picker"))
    jobs_p.add_argument("--range", dest="git_range", default=None)

    prep = sub.add_parser("prepare", help="copy one job into a temp parent")
    prep.add_argument("--repo", required=True, type=_repo)
    prep.add_argument("--surface", required=True, choices=("changes", "codebase", "picker"))
    prep.add_argument("--kind", required=True, choices=("code", "plan"))
    prep.add_argument("--plan-dir", default=None)
    prep.add_argument("--parent", default=None)
    prep.add_argument("--bar", action="append", default=[], dest="bars")
    prep.add_argument("--range", dest="git_range", default=None)

    clean = sub.add_parser("cleanup", help="delete a nuclear-blind- parent dir")
    clean.add_argument("--parent", required=True)

    args = parser.parse_args(argv)
    try:
        if args.cmd == "jobs":
            payload = actions.jobs_payload(args.repo, args.surface, args.git_range)
        elif args.cmd == "prepare":
            parent = Path(args.parent).expanduser() if args.parent else None
            payload = actions.prepare(
                args.repo,
                surface=args.surface,
                kind=args.kind,
                plan_dir=args.plan_dir,
                parent=parent,
                bars=[Path(b) for b in args.bars],
                git_range=args.git_range,
            )
        else:
            actions.cleanup(Path(args.parent))
            payload = {"deleted": str(Path(args.parent).expanduser())}
        print(actions.dumps(payload))
    except GitError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
