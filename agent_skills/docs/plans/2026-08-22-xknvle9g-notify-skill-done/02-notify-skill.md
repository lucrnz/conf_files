# Stage 02: notify skill

## Status
done

## Description

Write the auto-invoke `notify` skill and its sidecar README: when the agent may ping, how it runs the CLI from stage 01, and (in the README only) first-run permission setup.

## Rationale

The CLI is unusable as a skill until the agent has a description that matches the cues and a thin body that states yield rules and the invoke line. Permission text has to live somewhere the skill can point at without absorbing it.

## Invariants

- `notify/SKILL.md` does not set `disable-model-invocation`.
- Permission and first-run steps appear only in `notify/README.md`. The skill may point at that file; it must not restate the steps.
- Default title is `notify-me`. Banner bodies stay brief and contain no questions.

## Risks

A vague description will miss `ping me` / `notify me`, or will fire with no cue. The description must list those phrases and `/notify`, and the body must say no cue means no ping.

## Implementation

### Files

- `notify/SKILL.md`
- `notify/README.md`

### Steps

1. Write `notify/SKILL.md` with frontmatter `name: notify` and a `description` that states it sends a desktop notification, lists trigger phrases `notify me`, `ping me`, and `/notify`, and does not set `disable-model-invocation`.
2. In the skill body, state the request-scoped cue, standalone vs attached timing, ping-each-yield (blocked, then finished success or failure), default title `notify-me`, user text wins, brief body, no questions in the banner.
3. Add a Mechanical CLI section: resolve the directory that contains this `SKILL.md` (follow a symlink), then `uv run --project <that-dir>/scripts/notify notify --title … --message …`. Never a cwd-relative `notify/scripts/notify` path.
4. State: CLI non-zero → mention the failure once in chat, do not retry, point the user at `README.md` in this skill directory. Do not copy permission steps into the skill.
5. Write `notify/README.md` as the only permission home: Script Editor Notification Center allow for `osascript`; optional `brew install terminal-notifier` and that app's own allow; Linux `notify-send` / session bus / notification daemon; Focus or DND can hide a banner even when the CLI exits 0. Include one human smoke-test example that uses the same CLI; do not invent flags.

### Verify

- Read `notify/SKILL.md`. Confirm frontmatter name, no `disable-model-invocation`, description contains `notify me`, `ping me`, and `/notify`, and the body has cue scope, yield rules, default title, no-questions, the uv invoke line, and a README pointer on failure.
- Grep `notify/SKILL.md` for Script Editor, `brew install`, Notification Center, and `notify-send` setup prose — those strings must not appear as instructions in the skill (a mere `README.md` pointer is fine).
- Read `notify/README.md`. Confirm both macOS identities (Script Editor and terminal-notifier), the Linux daemon/bus note, and the Focus/DND exit-0 caveat.

## Acceptance

- An agent that only reads `notify/SKILL.md` knows when to fire, what to put in `--title` / `--message`, how to invoke the CLI, and to point at `README.md` if it fails.
- A human who only reads `notify/README.md` can grant the right permission and smoke-test. The skill body does not duplicate that setup.
