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

## 3. Write stage files

Create `docs/plans/` if it does not exist.

Path (flat): docs/plans/{planNNN}-{YYYY-MM-DD}-{plan-slug}_{stageNN}-{stage-slug}.md

Examples:

docs/plans/003-2026-08-12-checkout-rewrite_01-extract-pricing.md
docs/plans/003-2026-08-12-checkout-rewrite_02-swap-payment-adapter.md

### Rules

- `{planNNN}`: 3-digit, zero-padded (`001`, `002`, …). New plan id = max existing `planNNN` under `docs/plans/` + 1 (or `001` if none).
- `{YYYY-MM-DD}`: today's date when writing (use the environment date; do not ask the user). Same date on every stage file of this plan.
- `{plan-slug}` / `{stage-slug}`: short kebab-case.
- `{stageNN}`: 2-digit, zero-padded (`01`, `02`, …). Stages of one plan start at `01` and increase in execution order.
- All stages of one plan share the same `{planNNN}-{YYYY-MM-DD}-{plan-slug}` prefix.

**Each file** must include these headings in this order (optional extra sections only after them):

```markdown
# Stage {stageNN}: {title}

## Status
pending

## Description

## Rationale

## Implementation
```

- Status: `pending` - you are not implementing, just planning
- Description: what this stage does
- Rationale: why this stage exists / its payoff (per-stage, not a copy of the whole-plan story).
- Implementation: how to do it. Keep judgment flexible; be concrete enough to execute later.

## 4. Stop

Do not implement code or otherwise execute the plan.

Summarize: list each stage path written with a one-line description, then stop.

