# Stage 03: write ADR

## Status
done

## Description

Create `docs/adr/` and write ADR 0001 recording that ask-user replaces the native questions tool, with cannot-open as the only fallback and cancel as a decline.

## Rationale

This invert reverses a surprising v1 decision. `context/design.md` is not living documentation; the why has to live in the project’s normal ADR home or the next agent will “fix” routing back to native-first.

## Invariants

- Follow `domain-modeling/ADR-FORMAT.md`: `docs/adr/NNNN-slug.md`, short title, 1–3 sentences of context/decision/why. Do not invent extra required sections.
- First ADR is `0001` because `docs/adr/` does not exist yet. Do not skip or reuse a number.
- Do not edit `domain-modeling/ADR-FORMAT.md`.

## Risks

A vague ADR that only says “we prefer ask-user” will not stop someone from restoring native-first. It must say the v1 order is what was rejected and that cancel is not a fallback.

## Implementation

### Files

- `docs/adr/`
- `docs/adr/0001-ask-user-replaces-questions-tool.md`

### Steps

1. Create `docs/adr/` if it is missing.
2. Write `docs/adr/0001-ask-user-replaces-questions-tool.md` using the ADR-FORMAT template. Title: `ask-user replaces the native questions tool`. Status frontmatter `accepted` (this revisits the v1 native-first decision). Body, in 1–3 sentences: desktop `ask-user` is the primary multiple-choice picker; a native questions tool runs only when the window cannot open (no display, uv/Qt failure, timeout, missing skill); cancel is a decline, not a second prompt; numbered chat is last resort. Then why: v1 preferred the native tool and left consumers saying “questions tool if available,” so the window never replaced a working native tool. Optional **Considered Options** only if it stays short: native-first (v1), ask-user-only with no native fallback, and this invert.

### Verify

- `docs/adr/0001-ask-user-replaces-questions-tool.md` exists and starts with `# ask-user replaces the native questions tool`.
- The file states primary = ask-user, fallback = cannot-open only, cancel = decline, and that v1 native-first is what this replaces.
- Status is `accepted`.
- No other `docs/adr/0001-*.md` exists. `domain-modeling/ADR-FORMAT.md` is unchanged.

## Acceptance

- A future reader who never opens this plan directory can see that native-first was deliberate v1 and is now rejected, and why cancel does not bounce to the questions tool.
