# Stage 01: ask-user routing

## Status
done

## Description

Invert `ask-user/SKILL.md` so the skill is the primary picker and the native questions tool is only a cannot-open fallback. Keep the mechanical CLI, JSON contract, exit table, and README pointer. Do not edit `ask-user/README.md`.

## Rationale

The catalog description and the opening routing sentences are why agents load this skill and what they do first. While those still say “prefer the native tool / load only when it is missing,” no consumer patch can make the invert true.

## Invariants

- `ask-user/SKILL.md` does not set `disable-model-invocation`.
- Mechanical CLI, stdin/stdout shapes, exit codes 0/2/4/6, ≥10 minute / 600000 ms block, no agent-supplied Other, recommended-first, and the `README.md` pointer stay.
- First-run, wheel-download, Wayland, and human smoke steps stay only in `ask-user/README.md`. This stage does not edit that file.

## Risks

A description that still keys off “questions tool is not available” will not load when the native tool exists, which is the case this invert is for.

Leaving “Exit 4 or 6 → numbered chat” in place would send a cancelled window into a second picker, against cancel-as-decline.

## Implementation

### Files

- `ask-user/SKILL.md`

### Steps

1. In `ask-user/SKILL.md` frontmatter, keep `name: ask-user` and do not set `disable-model-invocation`. Replace `description` with this wording (locked): `Present multiple-choice questions (N options + Other) in a desktop window. Use when you need the user to choose among options. Replaces \`ask_user_question\` / a questions tool; fall back to that tool only if this window cannot open. Use when the user runs \`/ask-user\`.`
2. Replace the body sentence that prefers the native questions tool and loads this skill only when that tool is missing. State: always use this skill when a pick is needed; it replaces `ask_user_question` / a questions tool; do not dual-fire. Keep: the window is self-contained; do not send an Other option; put the recommended option first.
3. Keep the Mechanical CLI section, stdin/stdout shapes, and the 0/2/4/6 exit table as they are (see [context/design.md](context/design.md)).
4. Replace the current “exit 4 or 6 → numbered chat” rule with the chain in [context/design.md](context/design.md): cannot-open (exit 4, or the CLI never starts: uv/Qt fail, timeout, missing skill) → questions tool if present, else numbered options in chat, do not retry the window; exit 6 → decline, do not fall back to the questions tool, the caller keeps its decline rule; exit 2 → report stderr, do not retry. Keep the pointer at `README.md` on non-zero exit.

### Verify

- Read `ask-user/SKILL.md`. Confirm frontmatter name, no `disable-model-invocation`, and the description is exactly the locked wording in Steps (includes `Replaces`, `ask_user_question`, `cannot open`, `/ask-user`, and does not say `is not available`).
- Confirm the body says this skill replaces the native tool, forbids dual-fire, treats exit 6 as decline, and sends cannot-open to the questions tool if present else numbered chat.
- Confirm the body still has no-agent-supplied-Other, recommended-first, the uv invoke line, the ≥10 minute / 600000 ms block, stdin/stdout shapes, exits 0/2/4/6, and a README pointer.
- `rg -n "Prefer the native|load this skill only when it does not|is not available" ask-user/SKILL.md` — no matches in the body or description (the locked description uses `cannot open`, not `is not available`).
- `rg -n "wheel-download|Wayland|libtk|printf|echo" ask-user/SKILL.md` — those must not appear as setup steps (a `README.md` pointer is fine).
- `git diff -- ask-user/README.md` is empty.

## Acceptance

- An agent that only reads `ask-user/SKILL.md` uses the window first, falls back to a questions tool only on cannot-open, treats cancel as a decline, and uses numbered chat as last resort.
- `ask-user/README.md` and the CLI are untouched.
