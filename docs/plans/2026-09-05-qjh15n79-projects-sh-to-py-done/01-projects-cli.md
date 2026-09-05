# Stage 01: projects CLI

## Status
done

## Description

Add the `projects` uv project with the ported `clear` / `sync` argparse CLI in [context/design.md](context/design.md) and lock it. Leave `scripts/bin/projects.sh` in place.

## Rationale

The shim cannot point at a project that does not exist. Building and verifying the console script first freezes the invoke line and the walk/remove/`uv sync` contract before PATH cutover.

## Invariants

- No runtime dependencies. `requires-python` is `>=3.11,<3.15`.
- No `tests/` directory, no pytest extra.
- Subcommands are `clear` and `sync` only. `-n` / `--dry-run` is not on `sync`.
- Lockfiles are never deleted. `shutil.rmtree` / `Path.unlink` only; no `rm -rf` via subprocess.
- `scripts/bin/projects.sh` is not deleted in this stage.

## Risks

A live `uv sync` against a real lockfile is slower than this stage needs. Verify uses `--help`, usage failures, a missing `--dir`, a dry-run `clear` on a temp tree, and a source read. Do not require a successful `uv sync` of a third-party project to mark the stage done.

## Implementation

### Files

- `scripts/py/projects/`
- `scripts/py/projects/pyproject.toml`
- `scripts/py/projects/uv.lock`
- `scripts/py/projects/src/projects/__init__.py`
- `scripts/py/projects/src/projects/cli.py`

### Steps

1. Write `scripts/py/projects/pyproject.toml` the same way as the other uv console-script projects in this repo: `uv_build>=0.12.3,<0.13.0`, `module-name = "projects"`, `module-root = "src"`, console script `projects = "projects.cli:main"`, `requires-python = ">=3.11,<3.15"`, `version = "0.1.0"`, empty `dependencies`, no `[dependency-groups]`.
2. Write `scripts/py/projects/src/projects/__init__.py` (empty or a one-line package docstring) and `scripts/py/projects/src/projects/cli.py` with argparse, prog `projects`, required subparsers `clear` and `sync`. Both take `--dir` (no short flag), default cwd. Only `clear` takes `-n` / `--dry-run`. Extra positionals or unknown flags, including `sync -n`, use argparse’s default exit `2`.
3. In `scripts/py/projects/src/projects/cli.py`, expand `~` on `--dir` and require an existing directory; otherwise print `root directory not found: <path>` to stderr and return `1`. Resolve to an absolute path before walking.
4. In that same file, implement discovery, `clear`, and `sync` exactly as specified in [context/design.md](context/design.md): prune names, artifact names, no-markers early exit `0`, artifact walk under the whole root, continue-and-summarize on `uv sync`, `shutil.which("uv")` before sync, `subprocess.run` list argv and no shell, `shutil.rmtree` / `Path.unlink` with no `rm -rf` via subprocess. Directory walks do not follow directory symlinks. Marker and `.coverage` hits must be regular files, not symlinks.
5. Generate `scripts/py/projects/uv.lock` with `uv lock --project scripts/py/projects/` so it is committed.

### Verify

- `uv run --project scripts/py/projects/ projects --help` exits 0 and mentions `clear` and `sync`.
- `uv run --project scripts/py/projects/ projects clear --help` mentions `--dir` and `--dry-run` / `-n`.
- `uv run --project scripts/py/projects/ projects sync --help` mentions `--dir` and does not mention `--dry-run`.
- `uv run --project scripts/py/projects/ projects` (no subcommand) exits `2`.
- `uv run --project scripts/py/projects/ projects sync -n` exits `2`.
- `uv run --project scripts/py/projects/ projects clear --dir /this/path/does/not/exist` exits `1` and prints to stderr.
- In a temp directory that contains only a `.venv` and no `pyproject.toml` / `package.json`, `uv run --project scripts/py/projects/ projects clear -n --dir <temp>` prints `No script projects found` and exits `0` without listing `.venv` as a removal.
- In a temp directory that contains a `pyproject.toml` and a `.venv`, `uv run --project scripts/py/projects/ projects clear -n --dir <temp>` exits `0`, lists the project, and lists the `.venv` under a dry-run heading. The `.venv` directory still exists afterward.
- Read `scripts/py/projects/src/projects/cli.py` and confirm: no `shell=True`, no `rm -rf` via subprocess, lockfiles are not in the artifact set, `uv sync` continues after a non-zero.
- Read `scripts/py/projects/pyproject.toml` and confirm `requires-python = ">=3.11,<3.15"`, empty `dependencies`, console script `projects = "projects.cli:main"`, and no pytest extra.
- Confirm `scripts/py/projects/uv.lock` exists and there is no `scripts/py/projects/tests/` tree.
- Confirm `scripts/bin/projects.sh` still exists and this stage did not add `scripts/bin/projects`.

## Acceptance

- `uv run --project scripts/py/projects/ projects clear|sync [--dir DIR]` is a working console script.
- Usage problems exit `2`. Missing root, missing `uv` on `sync`, a remove error, or any failed `uv sync` exit `1` with a message on stderr.
- No project markers → exit `0` and no deletes. `clear -n` does not delete. Sync failures are summarized; the walk does not stop on the first one.
- `scripts/bin/projects.sh` is still the PATH command. No tests were added.
