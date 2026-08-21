---
name: create-multi-stage-plan
description: Create a multi-stage plan by writing markdown documents
disable-model-invocation: true
---

# Create multi-stage plan

Input: the proposed changes in the current conversation, plus any docs, diffs, or paths the user points at.

## 1. Resolve decisions

Do not write plan files while any approach is still multi-option. A broken Files contract is still multi-option (see Files).

- Prefer the `grilling` skill until decisions are settled and the user confirms shared understanding.
- If grilling is not available, use the question tool; put a recommended option first on every multi-choice question.

## 2. Decompose

Split the work into atomic stages. Order by **dependency first**, then **impact** among independent stages. Stage number is execution order.

## 3. Write plan directory

Create `docs/plans/` if missing and always start a **new** plan directory (do not append).

```
docs/plans/{YYYY-MM-DD}-{id}-{plan-slug}-pending/
  context/design.md
  context/{attachment}
  {stageNN}-{stage-slug}.md
```

Write `context/` first (`design.md`, then attachments), then stage files.

Example: `docs/plans/2026-08-16-v1stgxr8-checkout-rewrite-pending/context/design.md`

### Naming

1. Resolve this skill’s directory (the directory that contains this `SKILL.md`; follow the symlink if reached via `~/.agents/skills/create-multi-stage-plan`). Then:

   `uv run --project <that-dir>/scripts/plan-id plan-id mint --plans-dir docs/plans --slug {plan-slug}`

   Never invoke with a cwd-relative `create-multi-stage-plan/scripts/plan-id` path from the target repo. `uv` is required.
2. Use the single stdout line as the directory basename. Create that directory.
3. If mint exits non-zero, stop and report stderr. Do not pick an id by hand. Do not invent `{id}` and do not derive it by scanning sibling prefixes.

- `{YYYY-MM-DD}` and `{id}` come from the mint CLI. Do not ask the user for a date. Do not pass `--date` on the normal path.
- `{plan-slug}` / `{stage-slug}`: short kebab-case. The CLI rejects any other slug.
- `{stageNN}`: 2-digit, zero-padded (`01`, `02`, …). Stages of one plan start at `01` and increase in execution order.
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

- Settled decisions: grilling outcomes as decisions, not a transcript
- Stage map: dependencies and why this order — not a file listing
- Out of scope / Assumptions: None if there are none

Do not copy `design.md` sections into stages. Stages may link to `design.md` or a `context/` attachment. Do not put Implementation steps, file lists, or Acceptance in `design.md`.

If a decision must live past this plan, add a stage that writes it to the project's normal docs/ADRs. Do not treat `design.md` as living documentation.

Attachments under `context/` only when they would bloat `design.md`; every attachment must be linked from `design.md`.

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
- Rationale: why this stage exists / its payoff (per-stage, not the whole-plan story)
- Invariants / Risks: None if none
- Files: exact repo-relative file paths this stage will create or change, and directory prefixes. A prefix ends with `/` and has at least one path segment; empty, `.`, and `/` are illegal. A path matches a file entry by exact equality; it is under a prefix iff it starts with that prefix. Every repo path named in that stage’s Steps must appear as an exact Files entry. `None` only when Steps name no path. A prefix authorizes later growth; it does not replace an exact entry for a path Steps already name.

Vague “it works” or TBD, empty Files, or `None` when Steps name a path, is not done planning — rewrite.

## 4. Stop

Do not implement code or otherwise execute the plan.

Summarize: `context/design.md`, each attachment, and each stage path with a one-line description. Stop.
