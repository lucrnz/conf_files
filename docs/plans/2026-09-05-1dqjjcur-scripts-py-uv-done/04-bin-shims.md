# Stage 04: bin shims

## Status
done

## Description

Add `sh` forwarders on `scripts/bin` so `rearchiver` and `transfer-files` resolve on `PATH` via the hardcoded `uv run --project` lines in [context/design.md](context/design.md).

## Rationale

Stages 02 and 03 are only reachable with `uv run --project`. The shims are the PATH cutover and must not exist until those console scripts are real.

## Invariants

- Shims are `#!/bin/sh`. They contain no Python and no argument parsing.
- Project paths are exactly `$HOME/.conf_files/scripts/py/rearchiver` and `$HOME/.conf_files/scripts/py/transfer-files`.
- `bashrc` is not edited. `scripts/bin` is already on `PATH`.

## Risks

A machine where this repo is not at `$HOME/.conf_files` will get a uv “project not found” from the shim. That is the settled path choice, not a bug to paper over with a relative lookup.

## Implementation

### Files

- `scripts/bin/rearchiver`
- `scripts/bin/transfer-files`

### Steps

1. Write `scripts/bin/rearchiver` as a `sh` script whose body is only `#!/bin/sh` and `exec uv run --project "$HOME/.conf_files/scripts/py/rearchiver" rearchiver "$@"`. Mark it executable (`chmod +x`).
2. Write `scripts/bin/transfer-files` the same way, with project `$HOME/.conf_files/scripts/py/transfer-files` and console script `transfer-files`. Mark it executable.

### Verify

- `test -x scripts/bin/rearchiver && test -x scripts/bin/transfer-files` is true.
- `head -2 scripts/bin/rearchiver` is `#!/bin/sh` and the `exec uv run --project "$HOME/.conf_files/scripts/py/rearchiver" rearchiver "$@"` line.
- `head -2 scripts/bin/transfer-files` is `#!/bin/sh` and the matching `transfer-files` `exec` line.
- `scripts/bin/rearchiver --help` exits 0 and matches `uv run --project scripts/py/rearchiver rearchiver --help`.
- `scripts/bin/transfer-files --help` exits 0 and matches `uv run --project scripts/py/transfer-files transfer-files --help`.
- Confirm this stage does not modify the project bashrc.

## Acceptance

- From a shell with `scripts/bin` on `PATH`, `rearchiver --help` and `transfer-files --help` work without typing `uv run`.
- Each shim is a two-line `sh` `exec` at the hardcoded `$HOME/.conf_files/scripts/py/<name>` path. `bashrc` is unchanged.
