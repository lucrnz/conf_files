**Archive.** Decisions in this file were current as of 2026-09-05 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# Scripts Python uv projects

## Goal

Turn the two leftover standalone Python files under `scripts/` into independent uv projects with rewritten flag-only CLIs, ignore common Python junk under `scripts/py/`, and expose each command through a `sh` shim on `scripts/bin` (already on `PATH`).

## Settled decisions

- Projects live at `scripts/py/rearchiver/` and `scripts/py/transfer-files/`. One `.gitignore` at `scripts/py/.gitignore` covers that tree.
- `requires-python = ">=3.11,<3.15"`. Independent projects (no workspace). `src/` + `[project.scripts]` + `uv_build`. Commit each `uv.lock`. Empty runtime deps. No tests, no pytest extra.
- Public commands are `rearchiver` and `transfer-files`. Module names are `rearchiver` and `transfer_files`.
- Flags only. argparse usage errors exit `2`. Operational errors print to stderr and exit `1`. Stop on the first file that fails.
- Internals use the modern stdlib (`pathlib`, `tempfile`, `shutil`, `hashlib`). No `rm -rf` via subprocess.
- `rearchiver`: `--level`/`-l` (int 0–9, default 9), `--target`/`-t` (required). Target is a `.zip` file or a directory walked recursively for `.zip` files. Call `7z` only; missing or non-zero is an error. Replace the original zip only after a successful recompress.
- `transfer-files`: `--ext`/`-e` (required, repeatable, comma-separated, leading dots stripped, case-insensitive), `--dest`/`-d` (required existing directory), `--verify`/`-V` (optional). Recurse from cwd, preserve relative paths, copy (not move), skip if the destination file already exists. `--verify` hashes source and dest after a copy and fails on mismatch; existing dests are still skipped with no hash.
- Shims live in `scripts/bin/` and hardcode `$HOME/.conf_files/scripts/py/<name>`.
- Original `scripts/rearchiver.py` and `scripts/transfer_files.py` are removed once the matching project exists.

## Design

`scripts/bin` stays the only `PATH` directory. Python source and lockfiles stay off `PATH` under `scripts/py/`. Each tool is `uv run --project <project> <console-script>`.

**Packaging.** Same shape as `agent_skills/notify/scripts/notify`: `uv_build>=0.12.3,<0.13.0`, `module-root = "src"`, version `0.1.0`, `dependencies = []`. `transfer-files` sets `module-name = "transfer_files"` because the distribution name is hyphenated. No `tests/`, no `[dependency-groups]`.

**rearchiver invoke**

```
uv run --project "$HOME/.conf_files/scripts/py/rearchiver" rearchiver --target PATH [--level N]
```

`--target` is required. Resolve it to an absolute path. Missing path, or a path that is neither a file nor a directory, is operational failure. A file whose suffix is not `.zip` (case-insensitive) is operational failure. A directory is walked without following directory symlinks; every regular file whose suffix is `.zip` is a job. A directory with no zips is success and prints nothing.

`--level` is an int. Values outside `0`–`9` are usage failure. Default is `9`.

Per zip: require `7z` on `PATH` (`shutil.which`); if missing, fail once. Extract with `7z x` into a `tempfile.TemporaryDirectory`. Recompress with `7z a -tzip -mx{level}` to a temp zip path. Only after that process exits 0, replace the original zip. `subprocess.run` list argv, no shell. Print one `Processing <path>` line per zip (absolute or the path the user handed in). First `7z` failure or replace failure stops the walk.

**transfer-files invoke**

```
uv run --project "$HOME/.conf_files/scripts/py/transfer-files" transfer-files --ext EXTS --dest DIR [--verify]
```

`--ext` is `append`. Each value is split on commas; tokens are stripped, a leading `.` is removed, then lowercased. After flattening, at least one non-empty extension is required or it is usage failure. `--dest` must exist and be a directory or it is operational failure.

Walk cwd without following directory symlinks. Files only. A file matches when `Path.suffix` without the dot, lowercased, is in the extension set. Destination is `dest / relative-to-cwd`. Create parent directories as needed. If that dest file already exists, skip (no copy, no hash). Otherwise `shutil.copy2`, print a `>Copying <relative>` line. If `--verify`, sha256 both files in chunks; on mismatch delete the dest copy just written and fail.

If dest resolves inside cwd, do not treat dest itself or any path under it as a source. That stops `transfer-files --dest ./out` from copying `out/` back into itself.

**Shims.** `#!/bin/sh` and a single `exec`:

```
exec uv run --project "$HOME/.conf_files/scripts/py/rearchiver" rearchiver "$@"
```

and the same for `transfer-files` / `transfer-files`. Executable bit set. No other logic.

**gitignore.** `scripts/py/.gitignore` ignores `__pycache__/`, `*.py[cod]`, `.venv/`, `venv/`, `*.egg-info/`, `dist/`, `build/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.coverage`, `htmlcov/`. It does not ignore `uv.lock` or source.

## Stage map

1. **gitignore** — later stages run `uv lock` / `uv run` under `scripts/py/`. The ignore file must exist first so caches and venvs never show up as worktree noise.
2. **rearchiver CLI** — first project. It owns the 7z rewrite and deletes `scripts/rearchiver.py`. Nothing on `PATH` yet; invoke is `uv run --project`.
3. **transfer-files CLI** — second project, same packaging contract, different product. Deletes `scripts/transfer_files.py`. Independent of stage 02 except that the ignore file and the packaging pattern already exist.
4. **bin shims** — PATH cutover. Only makes sense once both console scripts exist at the hardcoded project paths.

## Out of scope

- Tests, pytest, a uv workspace, PEP 723 inline scripts
- Changing `bashrc` (`scripts/bin` is already on `PATH`)
- Rewriting or moving the non-Python files already in `scripts/bin/`
- Recursing into dest when dest is outside cwd (only the dest-inside-cwd skip applies)
- Supporting archive formats other than zip, or any 7-Zip binary other than `7z`
- Moving files instead of copying; flattening dest paths
- An ADR (this is local script packaging, not a repo-wide decision other trees must cite)

## Assumptions

- `uv` and, for `rearchiver`, `7z` are on the machine that runs the tools. Implementers may verify `7z` missing-path without running a live recompress.
- Directory walks do not follow directory symlinks. Matching is suffix-based and case-insensitive.
- argparse’s default extra-positional / unknown-flag behavior is enough; no custom `parse_known_args`.
- A successful no-op (directory with no zips, or no matching files to copy) exits `0`.
- The repo continues to live at `$HOME/.conf_files` on machines that use the shims.
