# Stage 02: CLI I/O

## Status
done

## Description

Add the `ask-user` console-script entry: stdin JSON, stdout JSON, argv, the 0/2/4/6 exit table, and a display probe. The wizard is an injectable hook behind a stub so tests never open a window.

## Rationale

The skill will only shell out. Locking I/O and exits here freezes the invoke line and the fallback codes that stage 04 will document, without waiting on Qt widgets.

## Invariants

- `cli.py` must not import `PySide6` at module level. Qt is imported only inside the display/`QApplication` path, and tests never take that path.
- Payload is stdin only. No `--file`, no argv JSON. Unknown args are exit 2. `-h` / `--help` may exit 0.
- Success prints only the encoded answers document on stdout. Errors go to stderr. Exit 4 and 6 print no answers JSON.
- The stub `wizard.py` must not import Qt. A live un-mocked run of `run_wizard` may raise `NotImplementedError`; tests always monkeypatch it.

## Risks

The default agent command timeout (~120s) will background this process once the real window exists. This stage cannot fix that; stage 04 must state the ≥10 minute block. Do not add a CLI-side timeout.

## Implementation

### Files

- `ask-user/scripts/ask-user/src/ask_user/cli.py`
- `ask-user/scripts/ask-user/src/ask_user/wizard.py`
- `ask-user/scripts/ask-user/tests/test_cli.py`

### Steps

1. Write `ask-user/scripts/ask-user/src/ask_user/wizard.py` as a stub: `run_wizard(payload) -> list[Answer] | None` with no Qt import, raising `NotImplementedError`. Stage 03 replaces this body.
2. Write `ask-user/scripts/ask-user/src/ask_user/cli.py` with `EXIT_OK = 0`, `EXIT_USAGE = 2`, `EXIT_NO_DISPLAY = 4`, `EXIT_CANCELLED = 6`, and `main(argv: list[str] | None = None) -> int`. Use argparse, prog `ask-user`, no payload flags. Extra positional or unknown optional args → stderr + `2`. `--help` uses argparse’s default exit.
3. In that same file, `main` reads all of stdin as UTF-8. Empty or invalid text, or `PayloadError` from `loads`, → stderr + `2` and do not call the display probe or the wizard.
4. In that same file, implement `display_available() -> bool`: on Linux (`sys.platform.startswith("linux")`) return True only when `DISPLAY` or `WAYLAND_DISPLAY` is a non-empty env var; on other platforms return True. If it returns False, print a one-line stderr message and return `4`.
5. In that same file, implement `ensure_application() -> int` that imports PySide6 lazily, constructs `QApplication` with `setApplicationName("ask-user")` if no instance exists, and returns `4` (with a stderr line) when import fails, construction fails, `screens()` is empty, or `platformName()` is `offscreen` or `minimal`, else `0`.
6. In that same file, `run_wizard` is a thin wrapper that calls `ask_user.wizard.run_wizard`. `main` order after a valid payload: `display_available` (False → `4`) → `ensure_application` (nonzero → that code) → `run_wizard`. `None` → exit `6` and no stdout JSON. A list of `Answer` → write `encode_answers(...)` to stdout and return `0`. Do not catch `NotImplementedError` as exit 4; that stub exists only until stage 03. Tests patch `display_available`, `ensure_application`, and `run_wizard` so pytest never constructs a `QApplication`.
7. Write `ask-user/scripts/ask-user/tests/test_cli.py` that never constructs a `QApplication`. Cover: valid stdin + patched `display_available` True + patched `ensure_application` no-op + patched `run_wizard` returning answers → exit 0, stdout is exactly `encode_answers` output; invalid JSON / reserved Other / extra argv → exit 2 and empty stdout; patched `display_available` False → exit 4, empty stdout, no `run_wizard` call; patched wizard returning `None` → exit 6, empty stdout; importing `ask_user.cli` does not import `PySide6`.

### Verify

- `uv run --project ask-user/scripts/ask-user --group dev pytest ask-user/scripts/ask-user/tests/test_cli.py ask-user/scripts/ask-user/tests/test_payload.py` exits 0.
- `uv run --project ask-user/scripts/ask-user ask-user --help` exits 0.
- `printf 'not-json' | uv run --project ask-user/scripts/ask-user ask-user` exits 2 and prints nothing on stdout.
- `uv run --project ask-user/scripts/ask-user ask-user extra` exits 2.
- Read `ask-user/scripts/ask-user/src/ask_user/cli.py` and confirm module-level code does not import PySide6, payload is stdin-only, and the exit constants are 0/2/4/6.
- Read `ask-user/scripts/ask-user/src/ask_user/wizard.py` and confirm it has no Qt import.

## Acceptance

- The invoke line `uv run --project <ask-user-skill-dir>/scripts/ask-user ask-user` is a working console script that reads stdin.
- Exit 2 on bad JSON or extra argv; exit 4 when the display probe fails; exit 6 when the wizard hook returns `None`; exit 0 prints only the answers JSON.
- Pytest never creates a `QApplication`. A live un-mocked wizard call is still a stub; that is expected until stage 03.
