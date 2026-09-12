# Stage 02: Wire SSH print

## Status
done

## Description

After the tunnel origin is known, `run_ssh_picker` prints `shorten(public) or public` on the `ask-user: ` line. The picker, fuse, and exits stay as they are. Every test that runs the real `run_ssh_picker` mocks `shorten` so CI cannot call v.gd.

## Rationale

Stage 01 can shorten but nobody prints the result. This is the only stage that makes the phone-copyable URL show up in chat.

## Invariants

- Exactly one stderr line starting with `ask-user: `. Nothing else on that line.
- On shorten success the remainder is the v.gd URL. On `None` it is `{origin}/t/{token}/`.
- Never print `127.0.0.1` or the ephemeral port.
- Exit table unchanged: 0 / 2 / 4 / 6. Shorten failure is not exit 4.
- `shorten` is imported inside `run_ssh_picker`, not at module top.
- Tests that reach `run_ssh_picker` patch `ask_user.shorten.shorten`. They do not call v.gd.

## Risks

The existing `test_ssh_mocked_tunnel_success` goes through the real `run_ssh_picker`. If it is not updated to patch `shorten`, pytest will make a live v.gd request. Patch that test in the same change as the call site.

## Implementation

### Files

- `ask-user/scripts/ask-user/src/ask_user/cli.py`
- `ask-user/scripts/ask-user/tests/test_cli.py`

### Steps

1. In `run_ssh_picker` in `ask-user/scripts/ask-user/src/ask_user/cli.py`, after `public = f"{tunnel.origin.rstrip('/')}/t/{token}/"` and before the stderr print, lazy-import `shorten` from `ask_user.shorten` and set `printed = shorten(public) or public`. Print `ask-user: {printed}`. Do not change bind / tunnel / serve / wait / teardown.
2. In `ask-user/scripts/ask-user/tests/test_cli.py`, patch `ask_user.shorten.shorten` in every test that uses the real `run_ssh_picker` (`test_ssh_mocked_tunnel_success`, `test_ssh_mocked_unused_timeout`, `test_ssh_mocked_cancel`) so those tests stay offline. Keep `test_ssh_mocked_tunnel_success` asserting one `ask-user: ` line whose URL is the long `https://example.trycloudflare.com/t/<64-hex>/` form by making the mock return `None`.
3. In that same file, add a test that the mock returns `https://v.gd/R709K6` and stderr is exactly one `ask-user: https://v.gd/R709K6` line (no trycloudflare host on that line). Add a test that `find_runner` is `None` and `shorten` is not called. Keep the existing unused-timeout → 4 / `not opened` and cancel → 6 tests.

### Verify

- `uv run --project ask-user/scripts/ask-user --group dev pytest ask-user/scripts/ask-user/tests` exits 0.
- Read `run_ssh_picker` in `ask-user/scripts/ask-user/src/ask_user/cli.py` and confirm `printed = shorten(public) or public`, lazy import, and unchanged `finally` teardown.
- `rg "urlopen|v.gd/create" ask-user/scripts/ask-user/tests/test_cli.py` has no hits; CLI tests mock `shorten`, they do not reimplement the HTTP client.

## Acceptance

- Mocked shorten success: the user-facing line is `ask-user: https://v.gd/R709K6`.
- Mocked shorten `None`: the user-facing line is the long secret Cloudflare URL, and the picker still exits 0 / 4 / 6 as before.
- No runner: `shorten` is not called; stderr is `no tunnel`; exit 4.
- Pytest does not contact v.gd or spawn `untun`.
