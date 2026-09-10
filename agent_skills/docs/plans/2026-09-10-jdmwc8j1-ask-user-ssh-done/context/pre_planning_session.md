**Archive.** Decisions in this file were current as of 2026-09-10 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# ask-user over SSH

Grilling-session capture that settled the product decisions. The plan-authoritative expansion is [design.md](design.md). Not living documentation.

## Goal

When the agent is in an SSH session and the native questions tool is missing, `ask-user` must still collect answers. Do not open the Qt window. Serve a 7.css wizard through a free `pnpx`/`npx` tunnel, put a secret in the URL path, have the agent relay that URL in chat, and keep the existing stdin/stdout/exit contract.

## Settled decisions

- **Fallback only.** Prefer the native questions tool when it exists. Do not dual-fire. Do not patch consumer skills.
- **SSH iff** any of `SSH_CONNECTION`, `SSH_CLIENT`, `SSH_TTY` is set, including loopback (personal-tailnet `127.0.0.1:2222` still counts).
- **Under SSH: never Qt**, even if `DISPLAY` / `WAYLAND_DISPLAY` is set. Not SSH: existing Qt path unchanged.
- **Both topologies.** SSH into a desktop host and SSH into a headless box.
- **Same invoke line.** `uv run --project <skill-dir>/scripts/ask-user ask-user`. CLI auto-switches. No `--ssh`, no second binary.
- **One uv project.** Extend `ask-user/scripts/ask-user`. No second package.
- **HTTP wizard** as the SSH happy path, not chat and not Qt.
- **Tunnel:** `pnpx` first, else `npx`. Pin `untun@latest`. No localhost / LAN / `ssh -L` / Tailscale serve as a user-facing path. Fail → exit 4 → chat.
- **Loopback origin only.** Bind `127.0.0.1` on an ephemeral port. Never print that address.
- **Secret in the path.** `https://<tunnel>/t/<token>/`. Anything else is 404.
- **URL delivery.** CLI prints one stderr line `ask-user: <url>` when the tunnel is up. Skill: relay that line in chat immediately, then wait for stdout JSON.
- **Unused fuse 10 minutes** until a JS beacon (`DOMContentLoaded` → `POST …/opened`). Prefetch/unfurl GET does not count. After the beacon: no CLI timeout.
- **No `pagehide`.** Explicit Cancel + Esc → exit 6.
- **Harness.** SSH path ≥ 4 hours (14400000 ms). Qt/local stays ≥ 10 minutes.
- **One HTML file + inline JS**, wizard parity, 7.css window chrome, quality bar is real.
- **7.css from unpkg** pinned `7.css@0.21.1` with native SRI on `<link rel="stylesheet">` (`integrity` + `crossorigin`). Not a `<script>`. SRI fail → unstyled, form still works.
- **Finish success:** tear down immediately, answers JSON, exit 0. No thank-you page.
- **Reuse exit 4** for no display, no runner, tunnel fail, unused fuse. stderr distinguishes. No fifth code.
- **Tests.** No `QApplication`. No real `untun` / Cloudflare in CI.

## Environment facts

- This grilling session’s Grok process was already in SSH: `personal-tailnet` sshd on `127.0.0.1:2222`, `SSH_TTY=/dev/ttys003`, `TERM=dumb`.
- Mac had a live Aqua session; Darwin’s display probe skips env and would try Qt on the wrong screen.
- No XQuartz. Personal-tailnet userspace: no `100.x` on a host interface; sshd is loopback + `tailscale serve`.
- `7.css@0.21.1` `dist/7.css` is self-contained (`url()` values are `data:` URIs). SRI on that one file covers the stylesheet.
- Agent tool commands in this harness are `TERM=dumb`; a TUI on `SSH_TTY` would fight the host TUI.
