"""argparse CLI: shorten one URL with v.gd."""

from __future__ import annotations

import argparse
import sys
from urllib.parse import urlparse

from shorten_url.client import shorten

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_FAIL = 4


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="shorten-url",
        description="Shorten a URL with v.gd.",
    )
    parser.add_argument("--url", required=True)
    args = parser.parse_args(argv)
    raw = args.url.strip()
    if not raw:
        print("url must be non-empty", file=sys.stderr)
        return EXIT_USAGE
    if any(ch.isspace() for ch in raw):
        print("url must not contain whitespace", file=sys.stderr)
        return EXIT_USAGE
    parsed = urlparse(raw)
    if parsed.scheme.lower() not in {"http", "https"}:
        print("url must start with http:// or https://", file=sys.stderr)
        return EXIT_USAGE
    existing = _passthrough(parsed)
    if existing is not None:
        print(existing)
        return EXIT_OK
    short = shorten(raw)
    if short is None:
        return EXIT_FAIL
    print(short)
    return EXIT_OK


def _passthrough(parsed) -> str | None:
    host = parsed.hostname
    if host is None or host.lower() != "v.gd":
        return None
    path = parsed.path
    if not path.lstrip("/"):
        return None
    if not path.startswith("/"):
        path = "/" + path
    query = f"?{parsed.query}" if parsed.query else ""
    fragment = f"#{parsed.fragment}" if parsed.fragment else ""
    return f"https://v.gd{path}{query}{fragment}"


if __name__ == "__main__":
    raise SystemExit(main())
