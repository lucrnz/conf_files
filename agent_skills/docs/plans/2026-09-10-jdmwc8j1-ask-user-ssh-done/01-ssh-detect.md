# Stage 01: SSH detect and CLI seam

## Status
done

## Description

Teach the existing `ask-user` CLI to recognize an SSH session and skip Qt. Under SSH, call an injectable `run_ssh_picker` that this stage implements as “unavailable” (exit 4, stderr `no tunnel`). Non-SSH behaviour stays the current display probe + wizard hook.

## Rationale

SSH on Darwin already tries WindowServer and can open a window on the wrong screen. Fail-fast to chat is the whole product until the tunnel exists, and the hook is the only safe place for stages 02–03 to plug in without touching Qt.

## Invariants

- `in_ssh_session()` is true iff any of `SSH_CONNECTION`, `SSH_CLIENT`, `SSH_TTY` is a non-empty environment variable. Loopback values count.
- When `in_ssh_session()` is true, `main` must not call `display_available`, `ensure_application`, or `run_wizard`.
- `cli.py` still does not import `PySide6` at module level. It does not import a future HTTP or tunnel module in this stage.
- Exit table stays 0 / 2 / 4 / 6. This stage uses 4 for the SSH stub, not a new code.
- Payload, argv, and the non-SSH path are unchanged.

## Risks

A stub that returns `None` would look like cancel (exit 6) and skip a useful stderr reason. The stub must be distinct from cancel: raise `NoPicker` (or equivalent) so `main` prints `no tunnel` and returns 4.

## Implementation

### Files

- `ask-user/scripts/ask-user/src/ask_user/cli.py`
- `ask-user/scripts/ask-user/tests/test_cli.py`

### Steps

1. In `ask-user/scripts/ask-user/src/ask_user/cli.py` add `in_ssh_session() -> bool` as specified in [context/design.md](context/design.md) (non-empty `SSH_CONNECTION` or `SSH_CLIENT` or `SSH_TTY`).
2. In that same file add `class NoPicker(Exception)` and `run_ssh_picker(payload) -> list[Answer] | None`. The stage-01 body of `run_ssh_picker` raises `NoPicker("no tunnel")` and does not import Qt, HTTP, or Node tools. Stage 03 replaces this body.
3. In `main`, after a valid payload and before the display probe: if `in_ssh_session()`, call `run_ssh_picker`. On `NoPicker`, print the exception message (or `no tunnel` if empty) to stderr and return `EXIT_NO_DISPLAY`. On `None`, return `EXIT_CANCELLED` with no stdout JSON. On a list of `Answer`, write `encode_answers(...)` to stdout and return `0`. If not in SSH, keep the existing `display_available` → `ensure_application` → `run_wizard` order.
4. Extend `ask-user/scripts/ask-user/tests/test_cli.py` (still never constructing `QApplication`): with `SSH_CONNECTION=127.0.0.1 1 127.0.0.1 2222` and valid stdin, `ensure_application` and `run_wizard` are not called and exit is 4 with `no tunnel` on stderr and empty stdout; the same with only `SSH_TTY` or only `SSH_CLIENT` set; with all three unset, the existing no-display / success patches still apply; empty-string SSH vars do not count as SSH; patched `run_ssh_picker` returning answers under SSH → exit 0 and encoded stdout; patched `run_ssh_picker` returning `None` under SSH → exit 6; importing `ask_user.cli` still does not import `PySide6`.

### Verify

- `uv run --project ask-user/scripts/ask-user --group dev pytest ask-user/scripts/ask-user/tests/test_cli.py ask-user/scripts/ask-user/tests/test_payload.py` exits 0.
- `printf '%s\n' '{"questions":[{"question":"Q","options":[{"label":"A"}]}]}' | env SSH_CONNECTION='127.0.0.1 1 127.0.0.1 2222' uv run --project ask-user/scripts/ask-user ask-user` exits 4, prints `no tunnel` on stderr, prints nothing on stdout, and does not start a Qt window.
- Unset SSH_* and re-run the existing extra-argv / invalid-JSON cases: still exit 2.
- Read `ask-user/scripts/ask-user/src/ask_user/cli.py` and confirm the SSH branch sits before `display_available`, and that `run_ssh_picker` raises `NoPicker` rather than returning `None`.

## Acceptance

- An SSH environment, including loopback `SSH_CONNECTION`, never opens the Qt wizard and exits 4 with `no tunnel`.
- A non-SSH environment is behaviourally identical to v1.
- Tests can replace `run_ssh_picker` without constructing `QApplication`.
