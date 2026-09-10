# Stage 03: untun bridge

## Status
done

## Description

Implement `tunnel.py` (pnpx/npx → `untun@latest` → public origin) and replace the stage-01 `run_ssh_picker` stub so the SSH branch binds the HTTP picker, starts the tunnel, prints the `ask-user: ` URL line, waits, and tears both down. CI never talks to Cloudflare.

## Rationale

Stage 01 owns the seam and stage 02 owns the page. This is the first stage that can actually collect answers over SSH, and the only one that is allowed to print a user-facing URL.

## Invariants

- User-facing URL is `{untun_origin}/t/{token}/`. Never print `127.0.0.1` or the ephemeral port.
- Runner is `pnpx` if present, else `npx`. Package is `untun@latest`. Child env includes `UNTUN_ACCEPT_CLOUDFLARE_NOTICE=1`.
- Missing runner, spawn failure, or no HTTPS origin within 120 seconds → stderr `no tunnel`, exit 4, HTTP server not left running.
- Unused fuse still maps to stderr `not opened` and exit 4 (`NoPicker`), not exit 6.
- Cancel still exit 6. Success still stdout JSON only, exit 0.
- `tunnel.py` does not import `PySide6`. Tests mock `which` and process spawn; they do not run `untun`.
- `run_ssh_picker` is the only new import site of `http_wizard` and `tunnel` in `cli.py`, and those imports stay inside the function.

## Risks

untun’s first run downloads `cloudflared` and can take longer than a naive parse loop. The 120-second origin wait is for that. Do not treat the download as a product failure if the URL arrives inside the window.

A leaked test that really calls `pnpx untun` will need network and will flake. Mock at the `tunnel` API boundary.

## Implementation

### Files

- `ask-user/scripts/ask-user/src/ask_user/tunnel.py`
- `ask-user/scripts/ask-user/src/ask_user/cli.py`
- `ask-user/scripts/ask-user/tests/test_cli.py`
- `ask-user/scripts/ask-user/tests/test_tunnel.py`

### Steps

1. Write `ask-user/scripts/ask-user/src/ask_user/tunnel.py` with `find_runner() -> str | None` (`shutil.which("pnpx")` or `shutil.which("npx")`) and `start_tunnel(port: int)` that spawns `[runner, "untun@latest", "tunnel", f"http://127.0.0.1:{port}"]` as specified in [context/design.md](context/design.md), reads the combined pipe until it sees an `https://` origin, and returns an object with `.origin` (no path) and `.close()` that SIGTERMs the process group (SIGKILL if it stays up). If `find_runner()` is `None`, `start_tunnel` raises a dedicated error the CLI maps to `no tunnel`. Origin wait longer than 120 seconds, or a non-zero exit before a URL, is the same class of error. Do not import Qt.
2. Replace the body of `run_ssh_picker` in `ask-user/scripts/ask-user/src/ask_user/cli.py`: generate `secrets.token_hex(32)`; construct the stage-02 `HttpPicker` with that token; `bind()`; `start_tunnel(port)` (on failure `shutdown()` the picker, raise `NoPicker("no tunnel")`); write `ask-user: {origin}/t/{token}/` plus newline to stderr and flush; `serve_in_thread()`; `wait()` inside `try`/`finally` that always `shutdown()` the picker and `close()` the tunnel. Map `UnusedTimeout` to `NoPicker("not opened")`. Return the `wait()` result (`list[Answer]` or `None`) otherwise.
3. Extend `ask-user/scripts/ask-user/tests/test_cli.py`: under SSH, patch `find_runner` / `start_tunnel` / `HttpPicker` (or patch `run_ssh_picker`’s collaborators) so a fake origin `https://example.trycloudflare.com` plus a picker that returns answers yields exit 0, empty extra stdout, and stderr containing exactly one `ask-user: https://example.trycloudflare.com/t/` line whose token is 64 hex chars; a picker that raises unused-timeout yields exit 4 and `not opened`; a picker that returns `None` yields exit 6; `find_runner` None yields exit 4 and `no tunnel` and does not bind a leaked server; the URL on stderr never contains `127.0.0.1`. Keep the stage-01 detection tests.
4. Write `ask-user/scripts/ask-user/tests/test_tunnel.py`: `find_runner` prefers `pnpx` when both exist, uses `npx` when only that exists, returns `None` when neither; `start_tunnel` invokes the runner with `untun@latest tunnel http://127.0.0.1:{port}` and `UNTUN_ACCEPT_CLOUDFLARE_NOTICE=1` (assert on a mocked `Popen`); a mocked pipe that emits `Tunnel ready at https://abc.trycloudflare.com` yields that origin; a mocked pipe that stays silent past a patched 0.05s wait errors; `close()` is called in those failure paths; importing `ask_user.tunnel` does not import `PySide6`.

### Verify

- `uv run --project ask-user/scripts/ask-user --group dev pytest ask-user/scripts/ask-user/tests` exits 0.
- Read `ask-user/scripts/ask-user/src/ask_user/cli.py` `run_ssh_picker` and confirm stderr format `ask-user: `, path `/t/{token}/`, `finally` teardown, and lazy imports.
- Read `ask-user/scripts/ask-user/src/ask_user/tunnel.py` and confirm no Qt import, pnpx-then-npx, and `UNTUN_ACCEPT_CLOUDFLARE_NOTICE`.
- `rg "127.0.0.1" ask-user/scripts/ask-user/src/ask_user/cli.py` — the only hits are the bind/untun origin argument, not an `ask-user: http://127.0.0.1` print.

## Acceptance

- SSH + mocked tunnel prints one `ask-user: https://…/t/<64-hex>/` line, then the usual 0 / 4 / 6 outcomes.
- There is no user-facing localhost URL and no fifth exit code.
- Pytest does not spawn `untun` or construct `QApplication`.
