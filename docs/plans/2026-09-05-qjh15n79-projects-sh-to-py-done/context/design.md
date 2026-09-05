**Archive.** Decisions in this file were current as of 2026-09-05 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# Migrate projects.sh to Python

## Goal

Replace `scripts/bin/projects.sh` with a uv project under `scripts/py/projects/` and a `scripts/bin/projects` shim, porting the existing `clear` / `sync` behavior to pathlib so it works on macOS.

## Settled decisions

- Project lives at `scripts/py/projects/`. Command name is `projects`. Shim is `scripts/bin/projects`. Delete `scripts/bin/projects.sh` once the shim exists.
- Packaging matches `rearchiver` / `transfer-files`: `requires-python = ">=3.11,<3.15"`, `src/` layout, `[project.scripts] projects = "projects.cli:main"`, `uv_build`, committed `uv.lock`, empty runtime deps, no tests. Do not touch `scripts/py/.gitignore` or `bashrc`.
- Subcommands `clear` and `sync`. `--dir DIR` on both, default cwd, `~` expanded. `-n` / `--dry-run` only on `clear`. `projects sync -n` is usage.
- Usage mistakes exit `2`. Operational failures exit `1`. Success is `0`.
- Faithful port of discovery, artifact names, skip-non-uv, continue-and-summarize on sync, and dry-run-on-clear-only. Replace GNU `find -printf` with `os.walk` / `pathlib`.
- No project markers under `--dir` → print `No script projects found under …` and exit `0`. `clear` does not run. Leftover artifacts stay.
- `clear` finds artifacts anywhere under `--dir` (only `.git` is pruned), not only inside discovered project directories.
- Shim hardcodes `$HOME/.conf_files/scripts/py/projects`. No Python and no argument parsing in the shim.

## Design

`scripts/bin` stays the only `PATH` directory. Python source and the lockfile stay off `PATH` under `scripts/py/projects/`. Invoke is `uv run --project <project> projects`.

**Packaging.** Same shape as `scripts/py/rearchiver`: `uv_build>=0.12.3,<0.13.0`, `module-name = "projects"`, `module-root = "src"`, version `0.1.0`, `dependencies = []`. No `tests/`, no `[dependency-groups]`. `scripts/py/.gitignore` already covers this tree.

**CLI.** argparse, prog `projects`, required subparsers.

```
projects clear [-n] [--dir DIR]
projects sync [--dir DIR]
```

`--dir` has no short flag. argparse’s `--dir=DIR` form is fine. Default is cwd. Expand `~`, then require the result to be an existing directory; otherwise print `root directory not found: <path>` to stderr and return `1`. Walk the resolved absolute path so printed roots are absolute.

Missing verb, unknown flag, or `sync -n` is argparse usage (exit `2`).

**Discovery.** Walk `--dir` without following directory symlinks. Do not descend into a directory whose name is one of:

`.git`, `node_modules`, `.venv`, `.cache`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `.next`, `.angular`, `.turbo`, `.parcel-cache`, `dist`, `build`, `coverage`, `htmlcov`

A directory is a discovered project when it contains a regular file named `pyproject.toml` or `package.json` (not a symlink). Sort unique paths. Print:

```
Discovered projects under <root>:
  <dir>
  …
```

If the list is empty, print `No script projects found under <root>` and return `0` before `clear` or `sync`.

**clear.** After the discovery listing, walk `--dir` again without following directory symlinks. Do not descend into `.git`. Collect, then sort:

- directories named `node_modules`, `.venv`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `coverage`, `htmlcov`, `.next`, `.vite`, `.angular`, `.turbo`, `.parcel-cache`, `.cache`, `dist`, `build` — record the directory and do not descend into it
- regular files named `.coverage`

Lockfiles (`uv.lock`, `package-lock.json`, `bun.lockb`, and any other lockfile) are never in this list and must not be deleted.

Print `Dry run: would remove:` or `Removing venvs and caches:`. If the list is empty, print `  nothing to remove` and return `0`. Otherwise print each path, and unless dry-run, `shutil.rmtree` directories and `Path.unlink` `.coverage` files. No `rm -rf` via subprocess. A remove error prints to stderr and returns `1`. Finish with `Total: N item(s) (dry run, nothing deleted)` or `Removed N item(s)`.

**sync.** After the discovery listing, `shutil.which("uv")` or print `'uv' not found in PATH` to stderr and return `1` (even if every project would be skipped). For each discovered dir, if both `pyproject.toml` and `uv.lock` exist as regular files, print `==> uv sync: <dir>` and run `subprocess.run(["uv", "sync"], cwd=dir)` with no shell. Non-zero increments failed and the walk continues. Otherwise increment skipped. Print `Summary: N synced, N failed, N skipped`. If any were skipped, list them under `Skipped (not uv projects):`. If any failed, list them under `Failed:` and return `1`.

**Shim.** `#!/bin/sh` and a single `exec`:

```
exec uv run --project "$HOME/.conf_files/scripts/py/projects" projects "$@"
```

Executable bit set. No other logic.

## Stage map

1. **projects CLI** — the uv project and the ported argparse program. Invoke is `uv run --project`. `projects.sh` stays on `PATH` so this stage cannot break the current command.
2. **bin shim** — PATH cutover. Only makes sense once the console script exists at the hardcoded project path. Deletes `scripts/bin/projects.sh`.

## Out of scope

- Tests, pytest, a uv workspace, PEP 723 inline scripts
- Changing `bashrc` or `scripts/py/.gitignore`
- Fail-loud stop on the first `uv sync` failure
- Narrowing `clear` to discovered project directories
- Running `clear` when no project markers exist
- Dry-run on `sync`, a `-d` short flag, or a flags-only CLI
- `npm` / `bun` install for JS projects
- Adding or removing artifact or prune names relative to `projects.sh`
- An ADR

## Assumptions

- `uv` is on the machine that runs `sync`. Implementers may verify the missing-`uv` path without running a live sync against a real lockfile.
- This repo lives at `$HOME/.conf_files` on the machines that use the shim.
- `scripts/bin` is already on `PATH`.
