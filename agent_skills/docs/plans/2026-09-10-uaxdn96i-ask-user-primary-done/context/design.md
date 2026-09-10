**Archive.** Decisions in this file were current as of 2026-09-10 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# ask-user replaces the native questions tool

## Goal

Make `ask-user` the primary multiple-choice picker. A native questions tool (`ask_user_question` or equivalent) runs only when the desktop window cannot open. Patch every consumer that still prefers the native tool. Record the invert as the first ADR.

## Settled decisions

Product decisions from the grilling session:

- **ask-user is primary.** Whenever the agent needs the user to choose among options, it loads this skill. It replaces `ask_user_question` / any questions tool. Do not use the native tool first. Do not dual-fire.
- **Cannot-open only falls back.** The fallback chain is: ask-user → uv/Qt (or other cannot-open) failure → native questions tool if available → else numbered options in chat. Cannot-open means exit 4, uv/Qt failure, timeout, or the skill/CLI never starts. Do not retry the window.
- **Cancel is a decline.** Exit 6 does not fall back to the questions tool. The calling skill keeps its decline rule: `archive-done-plans` stops; `nuclear-blind-review` goes sequential; `nuclear-review` still must not guess S/E.
- **Exit 2 is an agent bug.** Report stderr. Do not retry another picker.
- **Last resort is numbered chat.** After cannot-open, if no questions tool exists or that tool also fails, print numbered options in chat.
- **Patch all consumers.** `grilling`, `create-multi-stage-plan`, `implement-pending-plans`, `archive-done-plans`, `nuclear-review`, `nuclear-blind-review`. They name ask-user as the picker (`ask via ask-user`) and do not restate the exit-code chain.
- **grilling stays chat-then-window.** Print the round in chat, then ask via ask-user.
- **create-multi-stage-plan still prefers grilling.** If grilling is unavailable, it asks via ask-user directly (not the native questions tool).
- **Write ADR 0001** under `docs/adr/`. This reverses a surprising v1 decision (native tool first; do not patch consumers).
- **CLI, tests, `ask-user/README.md`, repo-root `README.md`, and `AGENTS.md` stay unchanged.** Routing is skill text. `AGENTS.md` already follows `ask-user/SKILL.md`.

Implementation-frontier decisions locked for this plan (not reopened):

- **Description wording** (frontmatter, so agents pick it up whenever they need a pick):

  > Present multiple-choice questions (N options + Other) in a desktop window. Use when you need the user to choose among options. Replaces `ask_user_question` / a questions tool; fall back to that tool only if this window cannot open. Use when the user runs `/ask-user`.

- **One home for the chain.** `ask-user/SKILL.md` owns when to fire, the cannot-open fallback, cancel-as-decline, exit 2, and numbered-chat last resort. Consumers only change the picker name.
- **No `disable-model-invocation`.** Unchanged.
- **Mechanical CLI, JSON shapes, exit table 0/2/4/6, ≥10 minute block, no agent-supplied Other, recommended-first, README pointer** stay as they are. Only the routing paragraphs change.
- **ADR path:** `docs/adr/0001-ask-user-replaces-questions-tool.md`. `docs/adr/` does not exist yet; create it. Follow `domain-modeling/ADR-FORMAT.md`. Status `accepted`.

## Design

`ask-user/SKILL.md` is the agent contract for picker routing. The CLI is unchanged.

### When to fire

The skill has no `disable-model-invocation`. The description lists the replace-the-native-tool trigger, the cannot-open fallback, and `/ask-user`.

Always run the CLI when a pick is needed. On exit 0, use the stdout answers.

**Cannot-open** (exit 4, or the CLI never starts): if a questions tool exists, use it now. Else numbered options in chat. Do not retry the window. Do not dual-fire with a window that already failed.

**Cancel** (exit 6): decline. Do not open the questions tool. The caller applies its own decline rule.

**Usage** (exit 2): report stderr, do not retry, point at `ask-user/README.md`.

The window stays self-contained (full question text, labels, descriptions) because not every caller prints first. `grilling` still prints the round in chat before opening the window.

### Consumers

Each consumer replaces “questions tool if available” / “question tool” / “Questions tool if available” with a pointer at ask-user. Decline and selection rules already in those skills stay.

| Skill | Ask site today | After |
| --- | --- | --- |
| `grilling` | after printing the round, use a questions tool if present | after printing the round, ask via ask-user |
| `create-multi-stage-plan` | grilling; else the question tool | grilling; else ask via ask-user |
| `implement-pending-plans` | ask (questions tool when available) | ask via ask-user |
| `archive-done-plans` | questions tool, `multi_select`; decline → stop | ask-user, `multi_select`; decline → stop |
| `nuclear-review` | Questions tool if available; else numbered and stop | ask via ask-user; do not guess |
| `nuclear-blind-review` | questions tool if available; decline → sequential | ask via ask-user; decline → sequential |

`grill-me` and `grill-with-docs` only delegate to grilling; they have no picker sentence of their own.

### ADR

The living why lives in `docs/adr/0001-ask-user-replaces-questions-tool.md`, not in this file. Short: desktop ask-user is primary because v1’s native-first routing meant the window never replaced a working questions tool; cancel is a decline so a closed window is not a second prompt.

## Stage map

1. **ask-user routing** — the chain has one home. Consumers cannot point at a skill that still says “prefer the native tool.” Highest impact: catalog description and body must invert before anything else is truthful.
2. **Patch consumers** — depends on stage 01’s wording. Until these six skills name ask-user, they still fire the native tool first and the invert does not happen.
3. **ADR** — no runtime dependency. Written last so the living record can name the skill as the how after that how exists. First ADR in the repo; creates `docs/adr/`.

## Out of scope

- CLI, wizard, payload, tests, new exit codes
- `ask-user/README.md`
- Repo-root `README.md` or `AGENTS.md`
- `grill-me` / `grill-with-docs` (they only run grilling)
- Editing the archived v1 plan under `docs/plans/2026-09-05-20av91yc-ask-user-done/`
- Rendering `preview`

## Assumptions

- `uv` is on machines that run the CLI. A cannot-start `uv` run is cannot-open.
- Agents load `ask-user` from the new description when they need a pick, not only when the native tool is missing.
- Consumer decline rules stay as written except the picker name.
- `docs/adr/` does not exist; the first ADR is `0001`.
- skill-design-principles apply: one home per fact; consumers do not copy the exit table.
