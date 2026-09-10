# Stage 02: patch consumers

## Status
done

## Description

Point every in-repo skill that still says “questions tool if available” (or equivalent) at ask-user. Do not copy the exit-code chain into those skills. Leave each skill’s decline and selection rules in place.

## Rationale

v1 left these skills saying “questions tool if available,” so they fire the native tool first even after stage 01. The invert only happens when they name ask-user.

## Invariants

- Consumers say `ask via ask-user` (or `ask-user` as the picker name). They do not restate exit 4/6, cannot-open, or numbered-chat last resort.
- Decline rules already in the consumer stay: `archive-done-plans` empty/declined → stop; `nuclear-blind-review` decline → sequential; `nuclear-review` do not guess S/E.
- `grill-me` and `grill-with-docs` are not edited.

## Risks

A leftover “questions tool if available” in any of the six files keeps that path on the native tool.

Restating the fallback chain in a consumer forks the contract away from `ask-user/SKILL.md`.

## Implementation

### Files

- `grilling/SKILL.md`
- `create-multi-stage-plan/SKILL.md`
- `implement-pending-plans/SKILL.md`
- `archive-done-plans/SKILL.md`
- `nuclear-review/SKILL.md`
- `nuclear-blind-review/SKILL.md`

### Steps

1. In `grilling/SKILL.md`, replace the closing sentence that uses a questions tool if the environment presents one. After presenting the round in chat, ask via ask-user. Keep printing the round first ([context/design.md](context/design.md)).
2. In `create-multi-stage-plan/SKILL.md`, keep “prefer grilling.” Replace “if grilling is not available, use the question tool” with “if grilling is not available, ask via ask-user.” Keep “recommended option first.”
3. In `implement-pending-plans/SKILL.md`, replace both “asks (questions tool when available)” / “ask with a list (questions tool when available)” with ask-via-ask-user wording. Keep the named-plan match keys and the several-plans list behavior.
4. In `archive-done-plans/SKILL.md`, replace “Ask …: questions tool, `multi_select`” with ask-user as the picker, still `multi_select`. Keep Archive-all as option 1, one option per listed plan, and empty-or-declined → stop.
5. In `nuclear-review/SKILL.md`, replace “Questions tool if available; else print numbered options and **stop** until answered” with “Ask via ask-user.” Keep “Do not guess.”
6. In `nuclear-blind-review/SKILL.md`, replace “ask parallel vs sequential (questions tool if available)” with “ask parallel vs sequential via ask-user.” Keep Recommended = parallel and Decline → sequential.

### Verify

- Read each file in Files. Confirm the ask site names ask-user and no longer tells the agent to prefer or wait for a questions tool.
- `rg -n -i "questions tool|question tool|ask_user_question" grilling/SKILL.md create-multi-stage-plan/SKILL.md implement-pending-plans/SKILL.md archive-done-plans/SKILL.md nuclear-review/SKILL.md nuclear-blind-review/SKILL.md` — no matches.
- `rg -n "ask via ask-user|ask-user" grilling/SKILL.md create-multi-stage-plan/SKILL.md implement-pending-plans/SKILL.md archive-done-plans/SKILL.md nuclear-review/SKILL.md nuclear-blind-review/SKILL.md` — each file has at least one match.
- Confirm `archive-done-plans` still stops on empty/declined, `nuclear-blind-review` still goes sequential on decline, `nuclear-review` still says do not guess, `grilling` still presents the round in chat before the picker.
- `git diff -- grill-me/SKILL.md grill-with-docs/SKILL.md` is empty.

## Acceptance

- The six consumer skills ask via ask-user. None of them still treat a native questions tool as the primary picker.
- Decline and selection rules in those skills are unchanged except the picker name.
- `grill-me` and `grill-with-docs` are untouched.
