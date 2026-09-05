# Stage 03: transfer-files CLI

## Status
done

## Description

Add the `transfer-files` uv project with the rewritten flag-only CLI in [context/design.md](context/design.md), lock it, and delete `scripts/transfer_files.py`.

## Rationale

Same packaging contract as stage 02, different product. Doing it second means the hyphenated distribution name / `transfer_files` module split is the only new packaging wrinkle, and the old script can disappear once the new command works.

## Invariants

- No runtime dependencies. `requires-python` is `>=3.11,<3.15`.
- No `tests/` directory, no pytest extra.
- Flags are `--ext`/`-e`, `--dest`/`-d`, and `--verify`/`-V` only. No positionals.
- Copy, do not move. Existing dest files are skipped and not hashed. `--verify` runs only after a copy this process just wrote.

## Risks

A full recurse+copy needs a throwaway cwd. Verify in this stage uses `--help`, usage failures, a missing dest, and a source read. A live copy is optional and must not target a real media directory.

## Implementation

### Files

- `scripts/py/transfer-files/`
- `scripts/py/transfer-files/pyproject.toml`
- `scripts/py/transfer-files/uv.lock`
- `scripts/py/transfer-files/src/transfer_files/__init__.py`
- `scripts/py/transfer-files/src/transfer_files/cli.py`
- `scripts/transfer_files.py`

### Steps

1. Write `scripts/py/transfer-files/pyproject.toml` the same way as stage 02, except `name = "transfer-files"`, `module-name = "transfer_files"`, and console script `transfer-files = "transfer_files.cli:main"`. `requires-python = ">=3.11,<3.15"`, empty `dependencies`, no `[dependency-groups]`.
2. Write `scripts/py/transfer-files/src/transfer_files/__init__.py` (empty or a one-line package docstring) and `scripts/py/transfer-files/src/transfer_files/cli.py` with argparse, prog `transfer-files`. `--ext`/`-e` required, `action="append"`. `--dest`/`-d` required. `--verify`/`-V` is `store_true`. Extra positionals or unknown flags use argparse’s default exit `2`.
3. In `scripts/py/transfer-files/src/transfer_files/cli.py`, flatten `--ext` values: split on commas, strip, strip one leading `.`, lowercase. If the set is empty, print a usage error to stderr and return `2`. Resolve `--dest` to an absolute path; if it is missing or not a directory, print to stderr and return `1`.
4. In that same file, implement the walk/copy/verify flow in [context/design.md](context/design.md): cwd walk without following directory symlinks; match on suffix; dest path preserves the relative path; `mkdir` parents; skip when dest exists; `shutil.copy2` otherwise and print `>Copying <relative>`; `--verify` sha256 both files in chunks, and on mismatch unlink the dest copy then return `1`. If dest is inside cwd, skip dest and everything under it as sources. Stop on the first failure.
5. Generate `scripts/py/transfer-files/uv.lock` with `uv lock --project scripts/py/transfer-files` so it is committed.
6. Delete `scripts/transfer_files.py`.

### Verify

- `uv run --project scripts/py/transfer-files transfer-files --help` exits 0 and mentions `--ext`, `--dest`, `--verify`, `-e`, `-d`, and `-V`.
- `uv run --project scripts/py/transfer-files transfer-files` (no flags) exits `2`.
- `uv run --project scripts/py/transfer-files transfer-files --ext mp4` (no `--dest`) exits `2`.
- `uv run --project scripts/py/transfer-files transfer-files --ext mp4 --dest /this/path/does/not/exist` exits `1` and prints to stderr.
- Read `scripts/py/transfer-files/src/transfer_files/cli.py` and confirm: comma + repeatable `--ext`, dest-inside-cwd skip, skip-if-exists, verify-after-copy only, unlink dest on hash mismatch, no `shell=True`.
- Read `scripts/py/transfer-files/pyproject.toml` and confirm `name = "transfer-files"`, `module-name = "transfer_files"`, console script `transfer-files = "transfer_files.cli:main"`, `requires-python = ">=3.11,<3.15"`, and no pytest extra.
- Confirm `scripts/py/transfer-files/uv.lock` exists and there is no `scripts/py/transfer-files/tests/` tree.
- Confirm `scripts/transfer_files.py` is gone.

## Acceptance

- `uv run --project scripts/py/transfer-files transfer-files --ext EXTS --dest DIR` is a working console script.
- Usage problems exit `2`. Missing dest, copy failure, or a `--verify` mismatch exit `1` with a message on stderr.
- Existing dest files are left untouched. A verify mismatch does not leave the bad copy. `scripts/transfer_files.py` is gone. No tests were added.
