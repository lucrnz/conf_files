# Stage 03: notify-me alias

## Status
done

## Description

Add the slash-only `notify-me` skill that delegates to `/notify`, same shape as `grill-me` → `grilling`.

## Rationale

`/notify-me` is the name the user asked for. The real contract already lives on `notify`; this file is only the grill-me-style alias so the slash menu has that name without a second copy of the rules.

## Invariants

- Body is exactly `Run the /notify skill` (no trailing commentary).
- `disable-model-invocation` is `true`.
- Do not restate cue rules, CLI flags, or permissions here.

## Risks

None

## Implementation

### Files

- `notify-me/SKILL.md`

### Steps

1. Create `notify-me/SKILL.md` as a slash-only alias: frontmatter `name: notify-me`, a short description that it is the slash alias for `/notify`, and `disable-model-invocation: true`.
2. Set the markdown body to exactly this line, with no other body text:

   `Run the /notify skill`

### Verify

- Read `notify-me/SKILL.md`. Confirm `name: notify-me`, `disable-model-invocation: true`, and that the body after the frontmatter is exactly `Run the /notify skill`.
- Confirm the file does not mention `osascript`, `terminal-notifier`, `--title`, or permission steps.

## Acceptance

- `/notify-me` is a slash-only alias that tells the agent to run the `/notify` skill.
- Cue policy and the CLI remain defined only in `notify/`.
