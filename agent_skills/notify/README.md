# notify

First-run setup for the `notify` skill. The agent invoke line and flags live in `SKILL.md`.

## macOS

The CLI uses `terminal-notifier` when it is on `PATH`, otherwise `osascript`.

### Script Editor (`osascript`)

`osascript` posts as Script Editor. The first run from a script often shows nothing and does not prompt.

1. Open Script Editor and run `display notification "test"`.
2. Allow the prompt.
3. Confirm **System Settings → Notifications → Script Editor** is on.

### terminal-notifier (optional)

```
brew install terminal-notifier
```

Allow **terminal-notifier** under **System Settings → Notifications**.

## Linux

Needs a session D-Bus and a notification daemon (GNOME, Plasma, dunst, mako, …). Install `notify-send` from your distro (`libnotify-bin` on Debian/Ubuntu, `libnotify` on Fedora/Arch). If `notify-send` is missing, the CLI falls back to `gdbus`.

## Smoke test

From this skill directory:

```
uv run --project scripts/notify notify --title notify-me --message test
```

## Focus / Do Not Disturb

A CLI exit of 0 means the helper returned 0. Focus, DND, or a denied permission can still hide the banner.
