---
name: notify
description: Send a desktop notification on macOS or Linux. Use when the user says notify me, ping me, or runs /notify.
---

# notify

Send one desktop banner when this request contains a cue (`notify me`, `ping me`, `/notify`). No cue, no ping. The next request does not inherit the cue.

## When

- Standalone cue: send immediately.
- Cue attached to a task: send each time you yield for this request — every blocked pause, then once when finished (success or failure).

## Banner

- `--title` defaults to `notify-me` unless the user gave exact title text.
- `--message` is one short status line. User-supplied text wins. Do not put questions in the banner; questions stay in the chat turn.

## Mechanical CLI

This skill lives in the directory that contains this `SKILL.md`. Follow the symlink if you reached it via `~/.agents/skills/notify`. Resolve that directory, then:

```
uv run --project <that-dir>/scripts/notify notify --title <title> --message <message>
```

Never invoke with a cwd-relative `notify/scripts/notify` path.

If the CLI exits non-zero: mention the failure once in chat, do not retry, and point the user at [README.md](README.md) in this skill directory.
