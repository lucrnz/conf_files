# Stage 02: HTTP wizard

## Status
done

## Description

Add a Qt-free loopback HTTP picker: token-prefixed routes, the 7.css single-page wizard, the opened beacon, the unused-fuse timer, Cancel/Esc, and Finish-time completeness. Do not spawn a tunnel and do not wire this module into `main` (that would publish localhost as a user path).

## Rationale

The page and the wait protocol are the bulk of the SSH UX and can be tested against `127.0.0.1` without npm or Cloudflare. Stage 03 only needs bind / wait / shutdown.

## Invariants

- `http_wizard.py` and `static/wizard.html` must not import `PySide6` or start `untun`.
- Completeness is `page_complete` / `first_incomplete` from `payload.py`. Do not fork those rules.
- GET of `/t/{token}/` does not mark the picker opened. Only `POST /t/{token}/opened` does.
- Default unused timeout is 600 seconds, overridable in the constructor so tests do not sleep 10 minutes.
- After the beacon, `wait` does not time out on its own.
- There is no `pagehide` handler in the HTML or JS.
- 7.css is the pinned `<link>` in [context/design.md](context/design.md) (version `0.21.1`, `integrity` + `crossorigin`). Question text is never assigned to `innerHTML`.
- Wrong token or path outside `/t/{token}/…` is 404.

## Risks

Chat unfurlers GET the URL. If GET disarms the fuse, a forgotten picker waits forever. The beacon POST is the only disarm.

User-controlled question strings in a public page are an XSS hole if interpolated into HTML. Embed JSON and paint with `textContent`.

## Implementation

### Files

- `ask-user/scripts/ask-user/src/ask_user/http_wizard.py`
- `ask-user/scripts/ask-user/src/ask_user/static/wizard.html`
- `ask-user/scripts/ask-user/tests/test_http_wizard.py`

### Steps

1. Write `ask-user/scripts/ask-user/src/ask_user/static/wizard.html` as one document: 7.css `<link>` exactly as in [context/design.md](context/design.md); a 7.css `.window` with title-bar text `ask-user`; a `Question N of M` label; a question body painted by JS; Recommended badge on the first option; Other row (radio/checkbox + text field enabled only when Other is on); Next / Back / Finish / Cancel buttons with Finish only on the last question and Back hidden on the first; inline error text `This question needs an answer.`; a `<script type="application/json" id="ask-user-payload">` placeholder `__ASK_USER_PAYLOAD__` and a token placeholder `__ASK_USER_TOKEN__`. Inline JS: `DOMContentLoaded` POSTs `{prefix}/opened`; Esc and Cancel POST `{prefix}/cancel`; Finish POSTs `{prefix}/submit` with the `encode_answers` JSON shape; on incomplete, stay on the first incomplete question and show the error; render labels and descriptions with `textContent` / `createElement` only. No `pagehide` listener.
2. Write `ask-user/scripts/ask-user/src/ask_user/http_wizard.py` with a `HttpPicker` (name may vary) that takes a `Payload`, a token string, and `unused_timeout_secs: float = 600`. `bind()` listens on `127.0.0.1` port `0` and returns the assigned port. `serve_in_thread()` starts `ThreadingHTTPServer` (or equivalent). Routes match the table in [context/design.md](context/design.md): GET `/t/{token}/` returns the template with placeholders replaced by `json.dumps` of the payload object and the raw token; GET `/t/{token}` redirects to `/t/{token}/`; POST `/opened` sets opened and cancels the unused timer (`204`); POST `/submit` parses JSON, builds `Answer` values, uses `first_incomplete` — incomplete `400`, complete stores answers and shuts down (`200`); POST `/cancel` stores cancelled and shuts down (`200`); anything else `404`. `wait()` blocks until shutdown: unused timer fired → raise a dedicated `UnusedTimeout` exception; cancel → `None`; answers → `list[Answer]`. `shutdown()` is idempotent and stops the server.
3. Write `ask-user/scripts/ask-user/tests/test_http_wizard.py` that never imports PySide6 and never calls `untun`. Cover: bind returns a port > 0; GET `/` or a wrong token is 404; GET `/t/{token}/` is 200 HTML containing the pinned 7.css href, the `integrity=` attribute, `crossorigin="anonymous"`, and `ask-user`; that GET leaves `opened` false; POST `/opened` then `opened` is true; submit with an incomplete set is 400 and `wait` is still blocked (use a short wait in a thread, or inspect state); submit with a complete set unblocks `wait` with matching `Answer` values; POST `/cancel` unblocks `wait` with `None`; `unused_timeout_secs=0.05` without `/opened` raises `UnusedTimeout`; after `/opened`, a `0.05` unused interval does not fire; importing `ask_user.http_wizard` does not import `PySide6`. Drive the server with `urllib` from the test process.

### Verify

- `uv run --project ask-user/scripts/ask-user --group dev pytest ask-user/scripts/ask-user/tests/test_http_wizard.py ask-user/scripts/ask-user/tests/test_cli.py ask-user/scripts/ask-user/tests/test_payload.py` exits 0.
- Read `ask-user/scripts/ask-user/src/ask_user/static/wizard.html` and confirm the exact 7.css URL + `sha384-WN2QoZVHe/0w3aOmuNlv18gZn4NKrLXxgsUtsLAXPV1zCE/49AFfl07gQ2knrObx`, no `pagehide`, no `innerHTML` assignments to payload fields, Cancel + Esc, and a `DOMContentLoaded` opened POST.
- Read `ask-user/scripts/ask-user/src/ask_user/cli.py` and confirm `run_ssh_picker` is still the stage-01 `NoPicker` stub (this stage does not wire HTTP into `main`).
- `rg PySide6 ask-user/scripts/ask-user/src/ask_user/http_wizard.py` prints nothing.

## Acceptance

- A test process can finish, cancel, and unused-timeout a picker on loopback without Qt and without a tunnel.
- GET does not count as opened; POST `/opened` does.
- The HTML is a 7.css window with wizard parity and a pinned SRI stylesheet.
- `main` is unchanged: SSH still exits 4 `no tunnel`.
