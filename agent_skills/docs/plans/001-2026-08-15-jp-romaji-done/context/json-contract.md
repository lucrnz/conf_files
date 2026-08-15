# scripts/romaji JSON and CLI contract

Plan-time attachment. After stage 01 this is implemented under `jp-romaji/scripts/romaji`. After stage 02, `SKILL.md` documents **skill-dir-relative** invoke only.

## Layout

```
jp-romaji/scripts/romaji/
  pyproject.toml
  uv.lock
  src/romaji/
    __init__.py
    cli.py
    pykakasi_engine.py
    cutlet_engine.py
  tests/
```

One uv project. Package `romaji`. Entry point `romaji` → `romaji.cli:main`.

Dependencies: `pykakasi`, `cutlet`, `fugashi`, `unidic-lite`. Dev: `pytest`. Hatchling (`uv init --package`).

## CLI

stdlib argparse only. `--help` required.

```
romaji [-h] [--engine {pykakasi,cutlet,both}] [FILE ...]
```

- `--engine` default: `both`
- Files, or stdin if none. Split on newlines; skip empty lines.
- JSONL stdout. Diagnostics stderr.
- Exit 0 on success. Non-zero on usage or engine failure.
- No house style.

Implementation / test from **repo root**:

```
uv run --project jp-romaji/scripts/romaji romaji --help
uv run --project jp-romaji/scripts/romaji pytest
```

Living skill invoke (stage 02 — not a cwd-relative `jp-romaji/...` path): resolve the directory that contains `SKILL.md` (follow the symlink), then:

```
uv run --project <that-dir>/scripts/romaji romaji --engine both
```

## JSONL record

`--engine both`:

```json
{
  "orig": "恋は戦争",
  "pykakasi": {
    "hira": "こいはせんそう",
    "kana": "コイハセンソウ",
    "romaji": "koiha senso",
    "tokens": [
      {"orig": "恋", "hira": "こい", "kana": "コイ", "romaji": "koi"},
      {"orig": "は", "hira": "は", "kana": "ハ", "romaji": "ha"},
      {"orig": "戦争", "hira": "せんそう", "kana": "センソウ", "romaji": "senso"}
    ]
  },
  "cutlet": {
    "hira": "こいはせんそう",
    "kana": "コイハセンソウ",
    "romaji": "koi wa sensou",
    "tokens": []
  }
}
```

- `orig` always present (line without trailing newline).
- Single-engine mode omits the other engine key.
- Each engine object: `hira`, `kana`, `romaji` (strings, `""` if unknown — never omit, never JSON `null`), `tokens` (array, may be `[]`).
- Token objects use the same four string fields.
- pykakasi must fill `tokens` from its convert API.
- cutlet may leave `tokens` as `[]`; line-level strings are still required.
- UTF-8.

## Engine settings

- pykakasi: Hepburn. Current convert API. Not Kunrei/Passport.
- cutlet: Hepburn. No house-style layer. Foreign-spelling defaults are fine; fusion votes on `hira`/`kana`.
- Same `orig` line to both.
