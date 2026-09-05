# Stage 01: scripts/py gitignore

## Status
done

## Description

Create `scripts/py/` and the ignore file that covers common Python, pytest, and cache paths for every uv project that will live under it.

## Rationale

Stages 02 and 03 run `uv lock` (and later `uv run`) in this tree. Ignoring venvs and bytecode first keeps those commands from leaving untracked junk.

## Invariants

- `uv.lock` and project source are not ignored.
- One ignore file only: `scripts/py/.gitignore`. No repo-root `.gitignore` in this stage.

## Risks

None

## Implementation

### Files

- `scripts/py/`
- `scripts/py/.gitignore`

### Steps

1. Create the `scripts/py/` prefix if missing and write `scripts/py/.gitignore` with exactly these patterns, one per line: `__pycache__/`, `*.py[cod]`, `.venv/`, `venv/`, `*.egg-info/`, `dist/`, `build/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.coverage`, `htmlcov/`.

### Verify

- `test -f scripts/py/.gitignore` is true.
- `git check-ignore -q scripts/py/rearchiver/.venv/bin/python` would match once that path exists; equivalently, read `scripts/py/.gitignore` and confirm it lists `.venv/` and `__pycache__/` and does not list `uv.lock`.
- `git status --short scripts/py/.gitignore` shows the new file as untracked or added, not ignored.

## Acceptance

- Anything created under `scripts/py/**/.venv/` or `scripts/py/**/__pycache__/` is ignored. `uv.lock` files under `scripts/py/` remain trackable.
