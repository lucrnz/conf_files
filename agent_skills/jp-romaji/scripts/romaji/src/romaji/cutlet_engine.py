"""cutlet/fugashi Hepburn conversion. Raw engine output, no house style."""

from __future__ import annotations

import cutlet
import jaconv

_cutlet = cutlet.Cutlet()


def _feat(value: object) -> str:
    if value is None or value == "*":
        return ""
    return str(value)


def convert(line: str) -> dict:
    words = list(_cutlet.tagger(line))
    tokens = []
    for word in words:
        kana = _feat(getattr(word.feature, "kana", None))
        tokens.append(
            {
                "orig": _feat(word.surface) or _feat(getattr(word, "surface", "")),
                "hira": jaconv.kata2hira(kana) if kana else "",
                "kana": kana,
                "romaji": _feat(_cutlet.romaji_word(word)),
            }
        )
    return {
        "hira": "".join(t["hira"] for t in tokens),
        "kana": "".join(t["kana"] for t in tokens),
        "romaji": _feat(_cutlet.romaji(line)),
        "tokens": tokens,
    }
