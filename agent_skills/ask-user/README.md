# ask-user

First-run setup for the `ask-user` skill. The agent invoke line, JSON contract, and exit codes live in `SKILL.md`.

## First run

The first `uv run` downloads the PySide6 wheel (large). That only needs a working `uv`; showing the window needs a graphical session.

## Display

Qt needs `DISPLAY` or `WAYLAND_DISPLAY`. It picks the platform plugin (Wayland or X11) from the session. If the window does not appear, check those env vars and that the Qt platform plugin loaded.

## SSH

Over SSH the CLI does not open Qt. It starts a tunneled page. The first SSH run uses `pnpx` (or `npx` if `pnpx` is missing) and will download `untun` plus `cloudflared`. The CLI accepts Cloudflare’s notice via its child environment; you do not answer a prompt.

The agent prints an `ask-user: ` HTTPS URL in chat. Open that URL. Do not open `127.0.0.1` or the ephemeral loopback port.

## Smoke test

From this skill directory:

```
printf '%s\n' '{"questions":[{"question":"Smoke?","options":[{"label":"Yes","description":"Window opened."}]}]}' | uv run --project scripts/ask-user ask-user
```

Finish the wizard (pick Yes, or Other with text). Cancel / Esc should print nothing and exit 6.
