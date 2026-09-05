# Stage 04: Skill and README

## Status
done

## Description

Write the auto-invoke `ask-user` skill and its sidecar README: when the agent may open the window, how it runs the CLI from stages 01–03, the timeout and fallback rules, and (in the README only) first-run display / PySide6 notes.

## Rationale

The CLI is unusable as a skill until the agent has a description that matches the missing-questions-tool trigger and a thin body that states the invoke line, the long block, and the exit fallbacks. First-run text has to live somewhere the skill can point at without absorbing it.

## Invariants

- `ask-user/SKILL.md` does not set `disable-model-invocation`.
- First-run, wheel-download, Wayland, and human smoke steps appear only in `ask-user/README.md`. The skill may point at that file; it must not restate those steps.
- Do not patch other skills. Do not edit the repo-root `README.md` or `AGENTS.md`.

## Risks

A vague description will miss the “questions tool is missing” case, or will dual-fire beside a working native tool. The description must list `ask_user_question` / questions tool not available and `/ask-user`, and the body must say prefer the native tool when it exists.

The default ~120s command timeout will background the modal if the skill forgets the ≥10 minute block.

## Implementation

### Files

- `ask-user/SKILL.md`
- `ask-user/README.md`

### Steps

1. Write `ask-user/SKILL.md` with frontmatter `name: ask-user` and this `description` (wording locked): `Present multiple-choice questions (N options + Other) in a desktop window when no questions tool is available. Use when you need the user to choose among options and \`ask_user_question\` / a questions tool is not available. Use when the user runs \`/ask-user\`.` Do not set `disable-model-invocation`.
2. In the skill body, state: prefer the native questions tool when it exists; load this skill only when it does not; do not dual-fire. The window is self-contained (full question text, labels, descriptions). Do not send an Other option; the CLI appends it. Put the recommended option first.
3. Add a Mechanical CLI section: resolve the directory that contains this `SKILL.md` (follow a symlink), then `uv run --project <that-dir>/scripts/ask-user ask-user` with the JSON payload on stdin. Never a cwd-relative `ask-user/scripts/ask-user` path. Set the shell/command tool timeout to at least 10 minutes (600000 ms if the tool uses milliseconds) so the process is not backgrounded. The CLI itself has no timeout.
4. In that same file, document the stdin JSON shape (`questions` / `options` / optional `multi_select`, `preview` allowed and ignored), the stdout `answers` shape (`selected` labels, `other` string or null), and the exit table 0 / 2 / 4 / 6 from [context/design.md](context/design.md). Exit 4 or 6 → fall back to numbered options in chat, do not retry the window. Exit 2 → report stderr, do not retry. Point at `README.md` in this skill directory on failure. Do not copy first-run setup into the skill.
5. Write `ask-user/README.md` as the only first-run home: first `uv run` downloads the PySide6 wheel; a graphical session is required (`DISPLAY` / `WAYLAND_DISPLAY`); Qt picks the platform plugin (Wayland or X11); if the window does not appear, check those env vars and the Qt platform plugin. Include one human smoke-test example that pipes a small JSON document into the same invoke line used in the skill (cwd-relative `scripts/ask-user` is fine in the README, matching `notify`). Do not invent flags.

### Verify

- Read `ask-user/SKILL.md`. Confirm frontmatter name, no `disable-model-invocation`, description contains `ask_user_question`, `questions tool is not available`, and `/ask-user`, and the body has fallback-only, no dual-fire, no agent-supplied Other, recommended-first, the uv invoke line, the ≥10 minute / 600000 ms block, stdin/stdout shapes, exits 0/2/4/6, fallback on 4 and 6, and a README pointer.
- Grep `ask-user/SKILL.md` for wheel-download, Wayland setup, `libtk`, and smoke-test `printf` / `echo` instructions — those must not appear as setup steps in the skill (a mere `README.md` pointer is fine).
- Read `ask-user/README.md`. Confirm the PySide6 first-run note, the display/Wayland env note, and one smoke command that uses stdin JSON and `uv run --project scripts/ask-user ask-user`.

## Acceptance

- An agent that only reads `ask-user/SKILL.md` knows when to fire, how to invoke the CLI, how long to block, what to put on stdin, how to read stdout, and to fall back in chat on exit 4 or 6.
- A human who only reads `ask-user/README.md` can get a first window on a graphical session. The skill body does not duplicate that setup.
- No other skill and no repo-root install doc was edited.
