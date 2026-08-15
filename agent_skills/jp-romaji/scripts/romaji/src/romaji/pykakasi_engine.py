"""pykakasi Hepburn conversion. Raw engine output, no house style."""

from __future__ import annotations

import pykakasi

_kakasi = pykakasi.kakasi()


def _s(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def convert(line: str) -> dict:
    tokens = []
    for item in _kakasi.convert(line):
        tokens.append(
            {
                "orig": _s(item.get("orig")),
                "hira": _s(item.get("hira")),
                "kana": _s(item.get("kana")),
                "romaji": _s(item.get("hepburn")),
            }
        )
    return {
        "hira": "".join(t["hira"] for t in tokens),
        "kana": "".join(t["kana"] for t in tokens),
        "romaji": "".join(t["romaji"] for t in tokens),
        "tokens": tokens,
    }
