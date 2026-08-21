# Stage 02: Review-time lint

## Status
done

## Description

Point plan-bar theme 7 at the Files contract. Keep planned ~1k on theme 5. Fold construction into primary question 9. Keep design judo as question 1. Stop refusing a construction-complete plan solely for a speculative simpler model.

## Rationale

The review loop is mostly leftover construction holes plus judo-as-a-gate. Lint Files; do not spend isolated passes inventing a new product.

## Invariants

- Theme 0 (design judo) remains primary question 1.
- Code-bar still applies to the would-be implementation. Do not copy code-bar rules into plan-bar.
- Files grammar is not restated; cite `create-multi-stage-plan`.
- No ninth theme. Theme 5 keeps planned ~1k. Theme 7 owns the Files contract.

## Risks

Reviewers may under-flag a genuinely muddy product model. That is accepted: Files held plus no-laundering plus ~1k is enough to approve; leftover product forks still fail theme 1.

## Implementation

### Files

- `nuclear-review/plan-bar.md`

### Steps

1. Extend theme 7 so a create-multi-stage-plan tree fails when a stage’s Steps name a path that is not an exact Files entry, Files is empty/`None` while Steps name a path, or Files contains an illegal prefix. Point at `create-multi-stage-plan` for the grammar.
2. Do not move planned ~1k off theme 5. Do not add a construction sermon there.
3. Keep primary question 1 (design judo). Fold “does Files hold” into question 9. Do not add question 10.
4. Change **Approval Bar** / **Do not approve** so “preserves a visible simpler design” is not a solo refuse. Do not approve when the Files contract is broken, a decision a later stage needs is unset, acceptance is uncheckable, scope is smuggled, the tree fit would fail code-bar (~1k, wrong layer, ignored helper), or the plan launders spaghetti.
5. Do not edit any other nuclear-review file.

### Verify

- Read `nuclear-review/plan-bar.md`. A construction-complete plan with a speculative “smaller product” note cannot hit a do-not-approve bullet for judo alone.
- A Steps/Files mismatch, illegal prefix, or planned ~1k owner is an explicit fail (theme 7 or theme 5).
- Grep: no duplicated Files grammar; `create-multi-stage-plan` is referenced; no theme 8.

## Acceptance

- Plan review can pass a Files-complete, non-laundering plan that a reviewer merely thinks could be a smaller product.
- Plan review cannot pass a create-multi-stage-plan tree that omitted exact Files entries for paths its Steps name, or that lists empty, `.`, or `/` as a prefix.
- `create-multi-stage-plan/SKILL.md` and `implement-pending-plans/SKILL.md` are untouched in this stage.
