**Archive.** Decisions in this file were current as of 2026-08-22 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# Notify skill

## Goal

Add a `notify` skill the agent auto-loads from a per-request cue, plus a `/notify-me` slash alias, so the agent can post a brief desktop banner on macOS (primary) and Linux (basic) through a small uv CLI.

## Settled decisions

- Two skills in this repo: `notify` is the real skill (auto-invoke). `notify-me` is a slash-only alias with `disable-model-invocation: true` whose body is exactly `Run the /notify skill`.
- The agent pings only when this request contains a cue: `notify me`, `ping me`, or `/notify`. No cue, no ping. The next request without a cue does not inherit one.
- Standalone cue → send immediately. Cue attached to a task → send each time the agent yields for that request: every blocked pause, then once when finished (success or failure).
- Banner is title + body + the macOS default notification sound. Linux is silent. Default title is `notify-me`. The agent composes a brief body; user-supplied text wins. The banner must not contain questions; questions stay in the chat turn.
- Implementation is a uv Python CLI at `notify/scripts/notify` (Python 3.11+, no runtime deps). Flags are `--title` and `--message` only, both required and non-empty.
- macOS: `terminal-notifier` if it is on `PATH`, otherwise `osascript` `display notification` with argv-passed strings and a short delay. Linux: `notify-send`, otherwise `gdbus` to `org.freedesktop.Notifications`. Any other OS fails.
- CLI non-zero on failure; the agent mentions the failure once in chat and does not retry. Exit 0 means the helper returned 0, not that the user saw a banner (Focus / DND / permission can drop it).
- No unit tests. Human setup and first-run permission live only in `notify/README.md`. `notify/SKILL.md` stays thin: when to fire, how to run the CLI, and a pointer at that README on failure.
- Click-to-focus, custom Notification Center app name or icon, subtitle, Linux sound, Windows, a signed `.app`, and a conversation-long ping flag are out.

## Design

`notify` is the agent contract. `notify-me` is the grill-me-style alias. The CLI is the only process that talks to the OS.

**Cue and yield.** The description on `notify` lists `notify me`, `ping me`, and `/notify` so the agent loads it without a slash. A cue is request-scoped. Each yield for that request is one CLI invocation. Body is one short status line (what finished, or that the agent is waiting). Never put the clarifying question in the banner.

**CLI.** Resolve the `notify` skill directory (follow a symlink). Then:

```
uv run --project <that-dir>/scripts/notify notify --title <title> --message <message>
```

Never invoke with a cwd-relative `notify/scripts/notify` path. `--title` and `--message` are required; whitespace-only is usage failure.

Dispatch:

| Platform | Order |
|---|---|
| macOS (`sys.platform == "darwin"`) | `terminal-notifier` on `PATH`, else `/usr/bin/osascript` (or `which osascript`) |
| Linux (`sys.platform.startswith("linux")`) | `notify-send` on `PATH`, else `gdbus` on `PATH` |
| anything else | fail, unsupported OS |

macOS `terminal-notifier` argv: `-title`, `-message`, `-sound default`. Do not pass `-activate`, `-open`, `-execute`, or `-sender`.

macOS `osascript`: feed the script on stdin; pass title then message as argv (never interpolate user text into AppleScript). Script: `display notification` of argv item 2 `with title` argv item 1 `sound name "default"`, then `delay 0.5`. No subtitle.

Linux `notify-send`: `-a notify-me -u normal --` title body.

Linux `gdbus`: session bus, `org.freedesktop.Notifications.Notify`, app name `notify-me`, empty icon, title, body, empty actions, empty hints, expire `-1`.

`subprocess.run` with a list argv, captured stdout/stderr, no `os.system`, no shell.

Exit codes: `0` helper returned 0; `2` usage; `3` unsupported OS; `4` no helper found; `5` helper non-zero (copy helper stderr). Errors go to stderr. Success prints nothing.

**Skills.** `notify/SKILL.md` has no `disable-model-invocation`. It states the cue/yield rules, the default title, the brief-body / no-questions rule, the uv invoke line, and that a failed CLI is mentioned once with a pointer to `README.md`. It does not restate permission steps or backend argv.

`notify/README.md` is the only home for first-run setup: Script Editor notification permission for `osascript`; optional `brew install terminal-notifier` and that app's own permission; Linux package / session bus / notification daemon; Focus can hide a banner on exit 0. A human smoke-test example may appear here; the agent-facing flag contract stays in `SKILL.md`.

`notify-me/SKILL.md` matches the grill-me shape: frontmatter name `notify-me`, `disable-model-invocation: true`, body exactly `Run the /notify skill`.

The repo-root install loop already symlinks every `*/SKILL.md` directory into `~/.agents/skills/`. No change to that loop.

## Stage map

1. **CLI** — the skills have nothing to run until the uv project exists and the dispatch/exit contract is locked.
2. **notify skill** — README and `SKILL.md` describe that CLI. They ship together so the failure pointer in the skill has a real README, and permission text is not stuffed into the skill.
3. **notify-me alias** — one-liner that only makes sense once `/notify` exists.

## Out of scope

- Click-to-focus, custom icon or Notification Center identity, subtitle, Linux sound, Windows, signed app bundle
- Unit tests, pytest, a `--dry-run` / `--sound` / `--no-sound` flag
- Conversation-scoped ping-until-stop
- Agent-initiated pings with no cue in the request
- Repo-root `README.md` or `AGENTS.md` edits
- An ADR (this is a new skill pair, not a repo-wide decision that other skills must cite)

## Assumptions

- `uv` is on the machine that implements and on machines that use the skill.
- After the files exist, install is the existing per-skill symlink loop in the repo `README.md`.
- macOS delivery requires a GUI login and Notification Center permission for Script Editor (osascript) or for terminal-notifier. Linux delivery requires a session bus and a notification daemon.
- Skill-design-principles apply: one home per fact, thin `SKILL.md`, no permission essay duplicated into the skill body.
