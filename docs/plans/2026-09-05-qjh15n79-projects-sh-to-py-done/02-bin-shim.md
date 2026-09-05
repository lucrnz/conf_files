# Stage 02: bin shim

## Status
done

## Description

Add the `sh` forwarder at `scripts/bin/projects` so `projects` resolves on `PATH` via the hardcoded `uv run --project` line in [context/design.md](context/design.md), and delete `scripts/bin/projects.sh`.

## Rationale

Stage 01 is only reachable with `uv run --project`. The shim is the PATH cutover and must not exist until that console script is real. Deleting `projects.sh` in the same stage avoids two commands that share a purpose.

## Invariants

- The shim is `#!/bin/sh`. It contains no Python and no argument parsing.
- The project path is exactly `$HOME/.conf_files/scripts/py/projects`.
- `bashrc` is not edited. `scripts/bin` is already on `PATH`.

## Risks

A machine where this repo is not at `$HOME/.conf_files` will get a uv “project not found” from the shim. That is the settled path choice, not a bug to paper over with a relative lookup.

## Implementation

### Files

- `scripts/bin/projects`
- `scripts/bin/projects.sh`

### Steps

1. Write `scripts/bin/projects` as a `sh` script whose body is only `#!/bin/sh` and `exec uv run --project "$HOME/.conf_files/scripts/py/projects" projects "$@"`. Mark it executable (`chmod +x`).
2. Delete `scripts/bin/projects.sh`.

### Verify

- `test -x scripts/bin/projects` is true.
- `head -2 scripts/bin/projects` is `#!/bin/sh` and the `exec uv run --project "$HOME/.conf_files/scripts/py/projects" projects "$@"` line.
- `scripts/bin/projects --help` exits 0 and matches `uv run --project scripts/py/projects/ projects --help`.
- `scripts/bin/projects` (no subcommand) exits `2`.
- Confirm `scripts/bin/projects.sh` is gone.
- Confirm this stage does not modify the project bashrc.

## Acceptance

- From a shell with `scripts/bin` on `PATH`, `projects --help`, `projects clear --help`, and `projects sync --help` work without typing `uv run`.
- The shim is a two-line `sh` `exec` at the hardcoded `$HOME/.conf_files/scripts/py/projects` path. `projects.sh` is gone. `bashrc` is unchanged.
