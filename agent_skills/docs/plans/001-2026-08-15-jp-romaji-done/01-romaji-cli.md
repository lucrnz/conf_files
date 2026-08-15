# Stage 01: Mechanical CLI and tests

## Status
done

## Description

Create `jp-romaji/scripts/romaji` as one uv package: argparse CLI, pykakasi + cutlet, JSONL, pytest. Contract: [json-contract.md](./context/json-contract.md).

## Rationale

The skill cannot invoke or parse a mechanical vote until this package exists. Tests lock the shape before `SKILL.md` is written.

## Invariants

- One project, one venv.
- stdlib argparse only.
- No house style in Python.
- Synthetic fixtures only.

## Risks

- `fugashi` / `unidic-lite` install failure: `blocked` with the installer error; do not stub cutlet.
- Engine APIs vary by version: wrap whatever `uv add` pins.

## Implementation

### Files

- `jp-romaji/scripts/romaji/pyproject.toml` (create)
- `jp-romaji/scripts/romaji/uv.lock` (create)
- `jp-romaji/scripts/romaji/src/romaji/__init__.py` (create)
- `jp-romaji/scripts/romaji/src/romaji/cli.py` (create)
- `jp-romaji/scripts/romaji/src/romaji/pykakasi_engine.py` (create)
- `jp-romaji/scripts/romaji/src/romaji/cutlet_engine.py` (create)
- `jp-romaji/scripts/romaji/tests/test_cli.py` (create)
- `jp-romaji/scripts/romaji/tests/test_engines.py` (create)
- `jp-romaji/scripts/romaji/tests/conftest.py` (create if needed)

### Steps

1. `uv init --package --name romaji` in `jp-romaji/scripts/romaji` (or equivalent hatchling + src layout). `requires-python = ">=3.11"`.
2. `uv add pykakasi cutlet fugashi unidic-lite` and `uv add --dev pytest`. **Write** `uv.lock` (do not git-commit in this stage).
3. Implement both engines and `cli.py` exactly as [json-contract.md](./context/json-contract.md).
4. Tests: `--help`; default `both`; each single engine; stdin; file; empty-line skip; JSON shape on `こんにちは`, `恋は戦争`, `コーヒー`, `してやんよ`, `I love you 愛してる`, `学校`. pykakasi `tokens` non-empty for `恋は戦争`. Allow cutlet `tokens` `[]`. At least one subprocess test of the console script. No house-style assertions. No network. No copyrighted lyrics.

### Verify

```
uv run --project jp-romaji/scripts/romaji romaji --help
printf '%s\n' 'こんにちは' '恋は戦争' | uv run --project jp-romaji/scripts/romaji romaji --engine both
uv run --project jp-romaji/scripts/romaji pytest -q
```

## Acceptance

- `--help` exits 0 and documents `--engine`. Default is `both`.
- JSONL matches [json-contract.md](./context/json-contract.md).
- `pytest -q` exits 0. Coverage listed in Steps is present.
- No house-style logic in `src/`.
- `uv.lock` exists. No git commit required.
