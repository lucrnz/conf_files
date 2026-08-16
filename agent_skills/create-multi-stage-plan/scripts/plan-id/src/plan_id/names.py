"""Validate slug/date, draw an id, retry if the basename is taken."""

from __future__ import annotations

import re
import secrets
from datetime import date
from pathlib import Path

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
ID_LEN = 8
RETRY_CAP = 16
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class MintError(Exception):
    pass


def draw_id() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(ID_LEN))


def validate_date(value: str) -> None:
    if DATE_RE.fullmatch(value) is None:
        raise MintError(f"invalid date: {value}")


def validate_slug(value: str) -> None:
    if SLUG_RE.fullmatch(value) is None:
        raise MintError(f"invalid slug: {value}")


def child_dir_names(plans_dir: Path) -> set[str]:
    if not plans_dir.is_dir():
        return set()
    return {p.name for p in plans_dir.iterdir() if p.is_dir()}


def mint(plans_dir: Path, slug: str, when: str | None = None) -> str:
    validate_slug(slug)
    day = when if when is not None else date.today().isoformat()
    validate_date(day)
    taken = child_dir_names(plans_dir)
    for _ in range(RETRY_CAP):
        candidate = f"{day}-{draw_id()}-{slug}-pending"
        if candidate not in taken:
            return candidate
    raise MintError("could not mint a unique basename")
