# Stage 03: Implement-time Files contract

## Status
done

## Description

Make `implement-pending-plans` treat the current stage’s Files as the only path set it may touch. Append a missing exact path when it sits under a listed prefix. Block when it would require a new prefix.

## Rationale

Approved plans ship below the bar because the implementer invents modules. Closing this stage’s Files at implement time is the other half of the write-time contract, without living-plan machinery.

## Invariants

- Status literals, selection, walk order, no auto-commit, and archive-when-all-done are unchanged.
- Files grammar and slash-bounded match are not restated; read this stage’s Files using the `create-multi-stage-plan` meaning.
- A path outside this stage’s Files uses existing `blocked` + stop later stages. No new status.

## Risks

A stage that listed a coarse legal prefix (e.g. `docs/`) makes many paths a quiet amend. Theme 5 / honest scope are supposed to catch that at plan review. Do not add a special-case denylist here.

## Implementation

### Files

- `implement-pending-plans/SKILL.md`

### Steps

1. In **Per stage**, after setting `in_progress` and before doing the work, apply this stage’s Files to every path the stage will create or change.
2. Path equals a Files file entry → continue. Path is under a Files prefix (trailing `/`, slash-bounded) → append the exact path to this stage’s Files, continue, include the added paths in **Summarize**. Otherwise → `blocked`, explain that the path is outside this stage’s Files, stop later stages, leave `*-pending`.
3. Implement may not add a prefix to Files. Parent directories of a listed file do not need their own entry and are not a block.
4. Do not read other stages’ Files or Stage map for authorization. Do not amend other stages or `design.md`. Do not add findings stages. Do not invoke nuclear-review. Do not change archive rules.
5. Point at `create-multi-stage-plan` for what a Files entry is. One or two sentences, not a recap of that skill.

### Verify

- Read `implement-pending-plans/SKILL.md`. The match/amend/block rule is in Per stage, applied after `in_progress` and before work. Summarize names the Files delta. Archive and selection text is unchanged.
- Grep: no restated Files grammar; no Stage map owners; no nuclear-review; no `*-done` policy change.
- Confirm `create-multi-stage-plan/SKILL.md` and `nuclear-review/plan-bar.md` are untouched in this stage.

## Acceptance

- An implementer following only this skill cannot add a path that is neither listed nor under a prefix in **this** stage’s Files without setting that stage `blocked`.
- An implementer can add a file under a listed prefix by appending that exact path to this stage’s Files and finishing the stage.
- Walk, archive, and selection behavior match pre-stage 03 except for the Files rule and the summary of amended paths.
