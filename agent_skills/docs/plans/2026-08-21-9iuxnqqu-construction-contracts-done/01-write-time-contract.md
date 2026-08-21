# Stage 01: Write-time contract

## Status
done

## Description

Put the Files contract in `create-multi-stage-plan` so a plan cannot be written when Steps name a path that Files does not list exactly, or when Files contains an illegal prefix.

## Rationale

Write-time is the only place that can stop underspec before nuclear review and before implement invents a tree. The other two skills need this file as the single source of truth.

## Invariants

- `design.md` still forbids Implementation, file lists, and Acceptance. Stage map stays dependencies and order — not owners, not a path inventory.
- Mint, directory shape, heading order, and “do not implement” are unchanged.
- A Steps/Files mismatch or an illegal prefix is the same class of block as leftover product forks: do not write files.

## Risks

A planner who does not know the paths will have to ask or grill instead of emitting `None` Files. That is intended.

## Implementation

### Files

- `create-multi-stage-plan/SKILL.md`

### Steps

1. In **1. Resolve decisions**, treat a broken Files contract as still multi-option: every repo path named in a stage’s Steps must be knowable as an exact Files entry, and every Files prefix must be legal, before any plan file is written.
2. Leave the **Stage map** bullet as dependencies and order, not a file listing. Do not add owners.
3. In the **Files** bullet, state the grammar: exact repo-relative file paths; directory prefixes that end with `/` and contain at least one path segment; empty, `.`, and `/` are illegal. Every path named in that stage’s Steps must appear as an exact Files entry. Allow `None` only when Steps name no path. Empty Files, or `None` when Steps name a path, is not done planning — same rewrite rule as vague Acceptance. A prefix authorizes later growth; it does not replace an exact entry for a path Steps already name.
4. Do not add examples, a cycle narrative, the implement match procedure, or plan-bar approval text.

### Verify

- Read `create-multi-stage-plan/SKILL.md`. Confirm the Files grammar, the Steps/Files rule, illegal prefixes, and refuse-to-write live in the existing sections (Resolve decisions, Files), not a new parallel heading stack.
- Confirm Stage map is still “not a file listing” and does not require owners.
- Confirm `design.md` heading list and “no file lists in design.md” are still there.
- Grep the file: no restated plan-bar approval text and no implement amend/block procedure.

## Acceptance

- A planner following only this skill cannot write a `docs/plans/*-pending` tree whose stage Steps name a path that is not an exact Files entry, or whose Files list contains empty, `.`, or `/`.
- `plan-bar.md` and `implement-pending-plans/SKILL.md` are untouched in this stage.
