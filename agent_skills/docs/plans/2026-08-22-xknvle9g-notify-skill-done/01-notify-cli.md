# Stage 01: Notify CLI

## Status
done

## Description

Add the uv project that sends one desktop notification given `--title` and `--message`, using the dispatch and exit codes in [context/design.md](context/design.md).

## Rationale

The skill and alias only shell out. Locking the CLI first freezes the invoke line, backends, and failure codes those files will document.

## Invariants

- No runtime Python dependencies. `requires-python` is `>=3.11`.
- Flags are `--title` and `--message` only. Both required; empty or whitespace-only is usage failure.
- No `tests/` directory, no pytest, no `--dry-run`.
- User-controlled strings never enter an AppleScript source string.

## Risks

`terminal-notifier` and `osascript` can exit 0 while Focus or a missing Notification Center permission hides the banner. The CLI must not pretend it confirmed visibility.

## Implementation

### Files

- `notify/scripts/notify/pyproject.toml`
- `notify/scripts/notify/uv.lock`
- `notify/scripts/notify/src/notify/__init__.py`
- `notify/scripts/notify/src/notify/cli.py`

### Steps

1. Write `notify/scripts/notify/pyproject.toml` the same way as the other uv console-script projects in this repo: `uv_build`, module `notify` under `src`, console script `notify = "notify.cli:main"`, no runtime `dependencies`, no `dev` pytest extra.
2. Write `notify/scripts/notify/src/notify/__init__.py` (empty or a one-line package docstring) and `notify/scripts/notify/src/notify/cli.py` with argparse: required `--title` and `--message`. Strip both; if either is empty, print a usage error to stderr and return `2`.
3. In `notify/scripts/notify/src/notify/cli.py`, dispatch: Darwin prefers `terminal-notifier` on `PATH` then `osascript`; Linux prefers `notify-send` then `gdbus`; any other `sys.platform` returns `3`. Missing helper returns `4`.
4. In that same file: macOS `terminal-notifier` argv `[-title, title, -message, message, -sound, default]`; macOS `osascript` script on stdin, title then message as argv, `display notification` + `sound name "default"` + `delay 0.5`; Linux `notify-send` argv `[-a, notify-me, -u, normal, --, title, message]`; Linux `gdbus` session `Notify` with app name `notify-me`, empty icon, expire `-1`.
5. Run helpers with `subprocess.run` list argv, `capture_output=True`, `text=True`. Helper non-zero → write its stderr (or stdout if stderr is empty) to stderr and return `5`. Helper zero → print nothing, return `0`.
6. Generate `notify/scripts/notify/uv.lock` with `uv lock` so it is committed.

### Verify

- `uv run --project notify/scripts/notify notify --help` exits 0 and shows `--title` and `--message`.
- `uv run --project notify/scripts/notify notify` (no flags) exits `2`.
- `uv run --project notify/scripts/notify notify --title '' --message hi` exits `2`.
- Read `notify/scripts/notify/src/notify/cli.py` and confirm the Darwin/Linux order, exact helper argv, no shell interpolation, and exit codes `0/2/3/4/5`.
- Confirm `pyproject.toml` has empty runtime dependencies and no pytest extra; confirm there is no `notify/scripts/notify/tests/` tree.
- Do not send a live notification as part of this stage's verify.

## Acceptance

- The invoke line `uv run --project <notify-skill-dir>/scripts/notify notify --title T --message M` is a working console script.
- A missing or blank flag exits `2`; unsupported OS exits `3`; no helper exits `4`; helper failure exits `5` with helper text on stderr; helper success is silent and exits `0`.
- macOS and Linux follow the backend order and argv in [context/design.md](context/design.md). No tests were added.
