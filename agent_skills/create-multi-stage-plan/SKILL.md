---
name: create-multi-stage-plan
description: Create a multi-stage plan by writing markdown documents
disable-model-invocation: true
---

# Create multi-stage plan

Input: the proposed changes in the current conversation, plus any docs, diffs, or paths the user points at.

## 1. Resolve decisions

Do not write plan files while any approach is still multi-option.

- Prefer the `grilling` skill until decisions are settled and the user confirms shared understanding.
- If grilling is not available, use the question tool; put a recommended option first on every multi-choice question.

## 2. Decompose

Split the work into atomic stages. Order by **dependency first**, then **impact** among independent stages. Stage number is execution order.

## 3. Write plan directory

Create `docs/plans/` if it does not exist. Always create a **new** plan (do not append stages to an existing plan directory).

```
docs/plans/{planNNN}-{YYYY-MM-DD}-{plan-slug}-pending/
  context/design.md
  context/{attachment}
  {stageNN}-{stage-slug}.md
```

Write `context/` first (`design.md`, then any attachments), then stage files.

Examples:

```
docs/plans/003-2026-08-12-checkout-rewrite-pending/context/design.md
docs/plans/003-2026-08-12-checkout-rewrite-pending/01-extract-pricing.md
docs/plans/003-2026-08-12-checkout-rewrite-pending/02-swap-payment-adapter.md
```

### Naming

- `{planNNN}`: 3-digit, zero-padded (`001`, `002`, …). New plan id = max `planNNN` already present on plan directories under `docs/plans/` (both `*-pending` and `*-done`) + 1, or `001` if none.
- `{YYYY-MM-DD}`: today's date when writing (use the environment date; do not ask the user).
- `{plan-slug}` / `{stage-slug}`: short kebab-case.
- `{stageNN}`: 2-digit, zero-padded (`01`, `02`, …). Stages of one plan start at `01` and increase in execution order.
- New plan directories always end in `-pending`.
- Stages are `{stageNN}-{stage-slug}.md` at the plan root only. Everything else goes under `context/`.

### context/design.md

Required headings in this order:

```markdown
# {plan title}

## Goal

## Settled decisions

## Design

## Stage map

## Out of scope

## Assumptions
```

- Goal: what this plan is for
- Settled decisions: grilling outcomes as decisions, not a transcript
- Design: whole-plan approach
- Stage map: dependencies and why this order — not a file listing
- Out of scope: whole-plan non-goals. `None` if there are none.
- Assumptions: whole-plan things treated as true. `None` if there are none.

Do not copy `design.md` sections into stages. Stages may link to `design.md` or to a `context/` attachment. Do not put Implementation steps, file lists, or Acceptance in `design.md`.

If a decision must live past this plan, add a stage that writes it to the project's normal docs/ADRs. Do not treat `design.md` as living documentation.

Optional attachments under `context/` only when they would bloat `design.md`. Every attachment **must** be linked from `design.md`.

### Stage files

Each stage file must include these headings in this order (optional extra sections only after them):

```markdown
# Stage {stageNN}: {title}

## Status
pending

## Description

## Rationale

## Invariants

## Risks

## Implementation

### Files

### Steps

### Verify

## Acceptance
```

- Status: `pending` — you are not implementing, just planning
- Description: what this stage does
- Rationale: why this stage exists / its payoff (per-stage, not the whole-plan story)
- Invariants: what must still be true after the stage. `None` if none.
- Risks: what can go wrong / what we are accepting. `None` if none.
- Files: paths this stage will create or change. `None` if no path changes.
- Steps: ordered actions
- Verify: commands/tests to run
- Acceptance: checkable conditions for done

Vague “it works” or TBD is not done planning — rewrite.

## 4. Stop

Do not implement code or otherwise execute the plan.

Summarize: `context/design.md`, each attachment, and each stage path with a one-line description. Stop.
