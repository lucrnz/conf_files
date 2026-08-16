# Stage 03: Plan bar and surface classification

## Status
done

## Description

Add `nuclear-review/plan-bar.md` and teach `nuclear-review/SKILL.md` to classify review surfaces and apply the matching bar(s). `/nuclear-review` stays in-session (no temp dir, no CLI). This is the source of classification rules later implemented by `blind-review jobs`.

## Rationale

The isolation skill cannot dispatch a plan job until the plan standard and the path test exist. Doing this on the in-session skill first gives one prose home for surfaces.

## Invariants

- Code rules still live only in `code-bar.md`.
- Plan-bar “would-be implementation” findings apply `code-bar.md` by link, not a copied checklist.
- Plans path is `docs/plans/` only.
- Mixed surfaces always produce both reviews. The in-session agent does not skip a surface.
- `scope=codebase` does not review `docs/plans/*-done`.

## Risks

- Classification rules written here will be re-implemented in Python in stage 04. Vague wording here becomes drift. Write them as path tests, not vibes.

## Implementation

### Files

- `nuclear-review/plan-bar.md` (create)
- `nuclear-review/SKILL.md` (edit)

### Steps

1. Write `plan-bar.md` in the same Rule / Flag / Remedy shape as `code-bar.md`, covering:
   - Design judo
   - No leftover multi-option decisions / TBD
   - Stage atomicity and dependency order
   - Checkable acceptance
   - Honest scope and explicit assumptions
   - Feasibility against the current tree
   - Do not launder a bad implementation through the plan
   - Extra flags when the file is a create-multi-stage-plan stage: `Status`, `Invariants`, `Acceptance` present and usable
   - Required section: apply [code-bar.md](code-bar.md) to the implementation this plan would produce; those findings are first-class
   - Primary questions and an approval bar that fail the review when any theme fires
2. In `SKILL.md`, after scope resolution, add surface classification:
   - Review surface paths under `docs/plans/` → plan surface, grouped by top-level `docs/plans/<dir>/` (one plan review per such dir).
   - Any other review-surface path → code surface.
   - Both non-empty → run both, in that session, as two labeled sections. No skip.
   - `scope=codebase`: code surface is the app tree omitting `docs/plans/`; plan surface is each `docs/plans/*-pending` directory (not `*-done`). Multiple pending plans → multiple plan sections (in-session: sequential sections; do not ask about subagent parallelism here).
   - `scope=changes` / `picker`: plan dirs are those actually in the surface, pending or done.
3. Point each section at the matching bar file. Output envelope: state scope, list surfaces, then one complete review per job. Shared tone stays in `SKILL.md`.

### Verify

- `plan-bar.md` links to `code-bar.md` and does not restate themes 0–7 of the code bar.
- `SKILL.md` states the path test, the per-`<dir>` grain, and the codebase `*-pending` rule in checkable language.
- Reading `SKILL.md` alone is enough to classify a mixed diff without guessing.

## Acceptance

- `/nuclear-review` on a code-only surface still uses only `code-bar.md`.
- `/nuclear-review` on a `docs/plans/`-only surface uses `plan-bar.md` and the would-be code-bar pass.
- `/nuclear-review` on mixed surfaces emits two reviews and does not drop one.
- `/nuclear-review scope=codebase` does not treat `*-done` plans as a review surface.
