# Stage 02: rearchiver CLI

## Status
done

## Description

Add the `rearchiver` uv project with the rewritten flag-only CLI in [context/design.md](context/design.md), lock it, and delete `scripts/rearchiver.py`.

## Rationale

The shim cannot point at a project that does not exist. Packaging and rewriting this CLI first freezes the invoke line and the 7z contract before `transfer-files` copies the packaging pattern.

## Invariants

- No runtime dependencies. `requires-python` is `>=3.11,<3.15`.
- No `tests/` directory, no pytest extra.
- Flags are `--level`/`-l` and `--target`/`-t` only. No positionals.
- The only 7-Zip binary is `7z`. The original zip is not replaced until recompress exits 0.

## Risks

A live recompress needs `7z` and a real zip. Verify in this stage uses `--help`, usage failures, a missing target, and a source read. Do not require a successful 7z round-trip to mark the stage done.

## Implementation

### Files

- `scripts/py/rearchiver/`
- `scripts/py/rearchiver/pyproject.toml`
- `scripts/py/rearchiver/uv.lock`
- `scripts/py/rearchiver/src/rearchiver/__init__.py`
- `scripts/py/rearchiver/src/rearchiver/cli.py`
- `scripts/rearchiver.py`

### Steps

1. Write `scripts/py/rearchiver/pyproject.toml` the same way as the other uv console-script projects in this repo: `uv_build>=0.12.3,<0.13.0`, `module-name = "rearchiver"`, `module-root = "src"`, console script `rearchiver = "rearchiver.cli:main"`, `requires-python = ">=3.11,<3.15"`, `version = "0.1.0"`, empty `dependencies`, no `[dependency-groups]`.
2. Write `scripts/py/rearchiver/src/rearchiver/__init__.py` (empty or a one-line package docstring) and `scripts/py/rearchiver/src/rearchiver/cli.py` with argparse, prog `rearchiver`. `--target`/`-t` required. `--level`/`-l` type `int`, default `9`. Extra positionals or unknown flags use argparse’s default exit `2`.
3. In `scripts/py/rearchiver/src/rearchiver/cli.py`, if `--level` is not in `0..9`, print a usage error to stderr and return `2`. Resolve `--target` to an absolute path. Missing path, or not a file or directory, prints to stderr and returns `1`. A file whose suffix (case-insensitive) is not `.zip` returns `1`.
4. In that same file, implement the per-zip 7z flow in [context/design.md](context/design.md): `shutil.which("7z")` or return `1`; extract into `tempfile.TemporaryDirectory`; recompress to a temp zip with `7z a -tzip -mx{level}`; replace the original only after exit 0; `subprocess.run` list argv, no shell. Directory targets walk without following directory symlinks and collect regular files with suffix `.zip`. Stop on the first failure. Print `Processing <path>` once per zip. No zips → return `0`.
5. Generate `scripts/py/rearchiver/uv.lock` with `uv lock --project scripts/py/rearchiver` so it is committed.
6. Delete `scripts/rearchiver.py`.

### Verify

- `uv run --project scripts/py/rearchiver rearchiver --help` exits 0 and mentions `--level`, `--target`, `-l`, and `-t`.
- `uv run --project scripts/py/rearchiver rearchiver` (no `--target`) exits `2`.
- `uv run --project scripts/py/rearchiver rearchiver --target . --level 99` exits `2`.
- `uv run --project scripts/py/rearchiver rearchiver --target /this/path/does/not/exist` exits `1` and prints to stderr.
- Read `scripts/py/rearchiver/src/rearchiver/cli.py` and confirm: `7z` only, temp-dir extract, replace-after-success, no `7za`, no `subprocess` `shell=True`, no `rm -rf`.
- Read `scripts/py/rearchiver/pyproject.toml` and confirm `requires-python = ">=3.11,<3.15"`, empty `dependencies`, console script `rearchiver = "rearchiver.cli:main"`, and no pytest extra.
- Confirm `scripts/py/rearchiver/uv.lock` exists and there is no `scripts/py/rearchiver/tests/` tree.
- Confirm `scripts/rearchiver.py` is gone.

## Acceptance

- `uv run --project scripts/py/rearchiver rearchiver --target PATH` is a working console script with default level 9.
- Usage problems exit `2`. Missing `7z`, missing target, non-zip file, or a failed 7z/replace exit `1` with a message on stderr.
- The original zip is not overwritten unless recompress succeeded. `scripts/rearchiver.py` is gone. No tests were added.
