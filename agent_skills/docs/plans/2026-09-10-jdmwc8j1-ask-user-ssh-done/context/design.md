**Archive.** Decisions in this file were current as of 2026-09-10 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# ask-user over SSH

## Goal

Give `ask-user` a first-class SSH path: detect an SSH session, skip Qt, serve the same questions in a tunneled 7.css wizard, and keep the existing stdin JSON → stdout JSON → exit 0/2/4/6 contract. Product decisions from the grilling session live in [pre_planning_session.md](pre_planning_session.md).

## Settled decisions

- **Fallback only.** Prefer the native questions tool. Load this skill only when that tool is absent. Do not dual-fire. Do not patch consumer skills; routing stays this skill’s catalog description and `SKILL.md`.
- **Same invoke line.** `uv run --project <ask-user-skill-dir>/scripts/ask-user ask-user`. Stdin JSON, stdout answers JSON. No `--ssh`, no `--file`, no argv payload, no second console script.
- **One uv project.** All new code lives in the existing `ask-user/scripts/ask-user` project (`ask_user` package, `ask-user` script). No second uv project under `scripts/`.
- **SSH detection.** `in_ssh_session()` is true when any of `SSH_CONNECTION`, `SSH_CLIENT`, or `SSH_TTY` is a non-empty env var. Loopback counts (personal-tailnet presents `127.0.0.1`).
- **Under SSH, never Qt.** Skip `display_available`, `ensure_application`, and `run_wizard`. A forwarded `DISPLAY` does not reopen the window.
- **Not SSH.** Existing Qt path unchanged (Linux env probe, then `QApplication`; Darwin/Windows still try the local session).
- **Both topologies.** SSH into a machine that has a desktop, and SSH into a headless box.
- **SSH happy path is HTTP + tunnel**, not chat and not a TUI. Chat is last resort (exit 4 or 6).
- **Tunnel runner.** `pnpx` if `PATH` has it, else `npx`. Pin package `untun@latest`. Command shape: `untun@latest tunnel http://127.0.0.1:<port>`. Set `UNTUN_ACCEPT_CLOUDFLARE_NOTICE=1` on the child so it does not prompt.
- **No user-facing localhost or LAN.** Do not tell the user to open `127.0.0.1`. Do not bind `0.0.0.0`. Do not document `ssh -L`. Do not call Tailscale serve. Missing runner, untun death, or no parsed URL → exit 4, stderr `no tunnel`.
- **Loopback origin.** HTTP listens on `127.0.0.1` with port `0` (kernel-assigned free port). That address is never printed.
- **Secret in the path.** Token is `secrets.token_hex(32)` (64 hex chars). Public URL is `{tunnel_origin}/t/{token}/`. GET/POST outside that prefix, or a wrong token, is 404.
- **Stderr URL line.** When the tunnel origin is known, write exactly one line to stderr and flush: `ask-user: {public_url}` where `{public_url}` is the full secret URL including `/t/{token}/`. Nothing else on that line. The skill tells the agent to relay it in chat immediately.
- **Unused fuse.** Until the opened beacon, a 600-second timer fires → shutdown, stderr `not opened`, exit 4. The interval is a named constant defaulting to 600 so tests can pass a short value.
- **Opened beacon.** The page’s JS, on `DOMContentLoaded`, `POST`s `{prefix}/opened`. That POST (not the HTML GET) cancels the fuse. After it, the CLI waits until Finish, Cancel, or Esc. No `pagehide` handler. No heartbeat cancel.
- **Cancel.** Visible Cancel button and document-level Esc → `POST {prefix}/cancel` → exit 6, no stdout JSON. Tab close does not cancel.
- **Finish.** Same completeness rules as Qt (`page_complete` / `first_incomplete` in `payload.py`). Incomplete set: stay up, jump the UI to the first incomplete question, show `This question needs an answer.` Complete set: tear down tunnel + HTTP immediately, print `encode_answers(...)` on stdout, exit 0. No thank-you page.
- **Harness timeouts.** Skill: if SSH_* will be set in the command environment, block ≥ 4 hours (`14400000` ms). Else ≥ 10 minutes (`600000` ms). The CLI has no timeout after the beacon; the unused fuse is the only CLI timer.
- **Page.** One HTML document + inline JS. Wizard parity: one question visible at a time, Next always enabled, Back except on question 1, Finish only on the last question, Recommended badge on the first option, Other row (single-select xor; multi-select extra), no option pre-selected. 7.css window chrome (`.window`, title-bar text `ask-user`, `Question N of M`).
- **7.css.** `<link rel="stylesheet" href="https://unpkg.com/7.css@0.21.1/dist/7.css" integrity="sha384-WN2QoZVHe/0w3aOmuNlv18gZn4NKrLXxgsUtsLAXPV1zCE/49AFfl07gQ2knrObx" crossorigin="anonymous">`. Pin that version URL. Do not use floating `https://unpkg.com/7.css`. Do not load 7.css as a `<script>`. SRI mismatch → browser drops the stylesheet; the form remains usable. Do not map SRI failure to exit 4.
- **XSS.** Question text, labels, descriptions, and Other values are rendered with `textContent` / `createElement` only. The payload is embedded as JSON in `<script type="application/json">`, not interpolated into HTML.
- **Exit table unchanged.** 0 success; 2 usage; 4 cannot present (no display / no tunnel / not opened); 6 cancelled. No fifth code. Exit 4 or 6 → chat fallback, do not retry. Exit 2 → report stderr, do not retry.
- **Tests.** Contract tests only. Never construct `QApplication`. Never spawn a real `untun` / `cloudflared` / network tunnel. Importing `ask_user.cli`, `ask_user.http_wizard`, and `ask_user.tunnel` must not import `PySide6`.
- **Docs split.** `SKILL.md` is the agent contract (when to fire, invoke, SSH vs local timeout, relay `ask-user: ` lines, JSON, exits). `README.md` is the only first-run home (PySide6 wheel, display, pnpx/`untun`/`cloudflared` download, Cloudflare notice, SRI pin). No repo-root `README.md` / `AGENTS.md` edit. No ADR.

## Design

`ask-user` remains one process and one console script. After a valid payload, `main` branches on `in_ssh_session()`.

```
parse argv → read stdin → loads (fail → 2)
  ├─ SSH_* set → run_ssh_picker
  │     find pnpx/npx (miss → 4, "no tunnel")
  │     bind HTTP 127.0.0.1:0
  │     start untun at that port (fail → 4, "no tunnel")
  │     stderr "ask-user: {origin}/t/{token}/"
  │     wait: unused 600s → 4 "not opened"
  │            beacon → wait for submit / cancel
  │     submit → stdout JSON, 0
  │     cancel / Esc → 6
  └─ else → display_available → ensure_application → run_wizard  (unchanged)
```

### Modules

Keep the v1 split. Add two Qt-free modules. `wizard.py` remains the only file allowed to import Qt.

| Module | Owns |
|---|---|
| `payload.py` | Unchanged. Parse, completeness, `encode_answers`. |
| `cli.py` | argv, stdin/stdout, exit table, `display_available`, `ensure_application`, `in_ssh_session`, `run_ssh_picker` orchestration. |
| `wizard.py` | `QWizard` only. |
| `http_wizard.py` | Loopback HTTP, token routes, unused timer, opened/submit/cancel, HTML injection. |
| `tunnel.py` | Locate `pnpx`/`npx`, spawn `untun@latest`, parse `https://` origin, kill the child. |
| `static/wizard.html` | Single-page template (7.css link, window chrome, placeholders only). |

`cli.py` and the new modules must be importable without `PySide6`. Import `http_wizard` and `tunnel` only inside `run_ssh_picker`.

### HTTP routes

Prefix `P = /t/{token}`.

| Method | Path | Effect |
|---|---|---|
| GET | `P/` | Wizard HTML. Does **not** cancel the unused fuse. |
| POST | `P/opened` | Beacon. Cancels the unused fuse. `204`. |
| POST | `P/submit` | JSON body in the `encode_answers` shape. Incomplete → `400`, stay up. Complete → store answers, shutdown, `200`. |
| POST | `P/cancel` | Shutdown as cancelled, `200`. |
| * | anything else | `404` |

GET `P` without a trailing slash redirects to `P/`.

### Tunnel

`tunnel.py` is a subprocess wrapper, not a Node library import.

1. `shutil.which("pnpx")` or, if missing, `shutil.which("npx")`. Neither → caller prints `no tunnel` and returns 4.
2. Spawn `[runner, "untun@latest", "tunnel", f"http://127.0.0.1:{port}"]` with `UNTUN_ACCEPT_CLOUDFLARE_NOTICE=1`, stderr merged into a pipe.
3. Read lines until a URL matching `https://[a-zA-Z0-9.-]+` appears (untun prints `Tunnel ready at https://….trycloudflare.com`). That origin has no path. Timeout on this wait is 120 seconds; miss → kill child, `no tunnel`.
4. `close()` sends SIGTERM to the process group, then SIGKILL if needed.

The public URL is `origin.rstrip("/") + "/t/" + token + "/"`.

### Page behaviour

Inline JS reads the JSON payload and token from the document. It paints one question at a time inside a 7.css `.window`. Next/Back change the visible question without talking to the server. Finish POSTs `encode_answers` JSON. The server is the source of truth for completeness; the client also uses the same rules so the jump-to-first-incomplete UX matches Qt before the POST.

Esc and the Cancel button POST `cancel`. They do not use `pagehide`.

### Skill contract additions

The invoke line does not change. The skill gains two mechanical duties on the SSH path:

1. If `SSH_CONNECTION`, `SSH_CLIENT`, or `SSH_TTY` is set in the environment the command will inherit, set the tool timeout to at least 4 hours (`14400000` ms). Otherwise keep ≥ 10 minutes.
2. As soon as stderr contains a line starting with `ask-user: `, print the remainder of that line to the user in chat. Keep waiting for the process. Do not treat the URL line as the answers document.

### Tests

Pytest drives `http_wizard` against `127.0.0.1` (implementation origin, not a product path). `tunnel.py` and the SSH branch of `cli.py` are tested with `which` and spawn mocked. A test asserts that a GET of `P/` leaves the unused fuse armed, and that POST `P/opened` disarms it. Unused-fuse tests pass a sub-second timeout.

## Stage map

1. **SSH detect + seam** — Until the CLI refuses Qt under SSH, every later picker is optional. This stage makes SSH fail fast to exit 4 (chat) via an injectable `run_ssh_picker`, and proves detection including loopback. No HTTP yet.
2. **HTTP wizard** — The page, routes, beacon, unused fuse, and completeness live behind a Qt-free module. Tests can hit loopback without a tunnel. Not wired to `main`; wiring without a tunnel would become a localhost user path, which is out of scope.
3. **untun bridge** — Depends on the HTTP module’s bind/wait/shutdown API and on the CLI seam from stage 01. This is the only stage that makes the SSH branch succeed. Mocks keep CI offline.
4. **Skill + README** — Document the relay line, the 4-hour SSH block, and first-run `pnpx`/`untun` only after those exist so the skill cannot describe a lie.

## Out of scope

- A second uv project or `ask-user-ssh` binary
- Patching grilling or other “questions tool if available” skills
- X11 / Wayland forwarding as a supported path
- localtunnel, wrangler, `cloudflared` invoked except as untun’s child
- Binding `0.0.0.0`, advertising `127.0.0.1`, `ssh -L`, or Tailscale serve
- TUI / `/dev/tty` / `SSH_TTY` pickers
- `pagehide` or heartbeat cancel
- A fifth exit code
- Rendering `preview`
- Thank-you page after submit
- Live `untun` / Qt in pytest
- Repo-root `README.md` or `AGENTS.md` edits
- An ADR
- Windows-only work (the skill stays Linux + macOS)

## Assumptions

- `uv` is on machines that implement and use the skill.
- SSH hosts that should get the picker have `pnpx` or `npx` and outbound HTTPS to npm and Cloudflare. Otherwise exit 4 → chat is correct.
- The user-facing browser can reach `*.trycloudflare.com` and `unpkg.com`.
- Anyone who has the full secret URL can submit until Finish or Cancel. The path token plus one-shot teardown is the control. Cloudflare edge logs see the path.
- First successful submit wins if two tabs share a token.
- Chat clients may GET the URL for unfurls; that must not count as opened.
- Default agent command timeout (~120s) will background the process unless the skill forces the long block.
- Skill-design-principles apply: one home per fact, thin `SKILL.md`, first-run only in `README.md`.
- The 7.css integrity hash in Settled decisions is `sha384` of `https://unpkg.com/7.css@0.21.1/dist/7.css` as retrieved on 2026-09-10. Re-fetch and confirm before baking it in; do not silently retarget the version.
