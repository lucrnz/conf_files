---
name: implement-pending-plans
description: >
  Implement pending multi-stage plan stages under docs/plans/ (from create-multi-stage-plan).
  Walk one plan in stage order; set Status in_progress → done or blocked. No automatic git.
  Use when the user runs /implement-pending-plans or asks to implement/execute pending plan stages.
disable-model-invocation: true
---

# Implement pending plans

Input: optional plan id, stage path, or “retry blocked”; else discover under `docs/plans/`.

Companion to `create-multi-stage-plan`. Stage path shape:

`docs/plans/{planNNN}-{YYYY-MM-DD}-{plan-slug}_{stageNN}-{stage-slug}.md`

Plan prefix = everything before `_{stageNN}-`.

## Status

Under `## Status`, the value is a single trimmed line. Exact literals (case-sensitive):

| Status | Meaning |
|--------|---------|
| `pending` | Not started |
| `in_progress` | Started, not finished |
| `blocked` | Cannot finish; needs human input or fix |
| `done` | Finished |

**Needs work:** `pending`, `in_progress`.  
**Skip:** `done`, and `blocked` unless the user asked to retry blocked (or named that blocked stage).

Unusable file (missing `## Status`, or value not one of the four): set `blocked` if you can write the file, explain, stop.

## 1. Discover and select

1. List stage files under `docs/plans/`.
2. Group by plan prefix. Read each file’s Status.
3. A plan is selectable if it has any stage that needs work (include `blocked` only when retry applies).
4. Selection:
   - User named a **stage path**: that stage only (if it needs work or is a retry target); then stop after it.
   - User named a **plan** (id, prefix, or slug): that plan.
   - Else if exactly one selectable plan: use it.
   - Else if several: ask with a list (questions tool when available); show pending/in_progress counts.
   - Else: report nothing to do, stop.

## 2. Walk stages

On the chosen plan, order stages by `{stageNN}` ascending.

Default: every stage that needs work, in order, without pausing between stages.

Do **not** auto-commit, branch, or open PRs.

## 3. Per stage

For each stage that needs work:

1. Set Status to `in_progress`.
2. Implement what the stage asks for (Description, Implementation, and any later sections). Not limited to code — do the work the stage describes.
3. If you cannot finish (underspecified, missing dependency, hard failure): set Status to `blocked`, explain to the user, **stop the plan** (do not continue later stages).
4. Otherwise set Status to `done` and continue.

## 4. Summarize

List stages completed this run, any blocked stage and why, and any remaining needs-work stages on that plan. Stop.
