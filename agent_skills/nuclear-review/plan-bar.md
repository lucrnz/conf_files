# Plan bar

Each theme: **rule** / **flag** / **remedy**. Apply all. Push hard — these are non-negotiable review pressures, not optional style notes.

Also apply [code-bar.md](code-bar.md) to the implementation this plan would produce. Those findings are first-class, not an afterthought. Do not copy code-bar rules here; follow that file.

## Review Themes

### 0. Design judo

- **Rule:** Prefer the design that is inevitable in hindsight. Do not plan to rearrange complexity. Delete a layer, a stage, or a concept when a simpler model would do.
- **Flag:** A plan that moves pieces around without reducing them; a pipeline whose stages exist to compensate for a muddy model.
- **Remedy:** Reframe the model so whole stages or branches disappear; plan the smaller thing.

### 1. Decisions settled

- **Rule:** No leftover multi-option forks. No TBD where the next stage would have to guess. If a choice is still open, the plan is not reviewable as a plan.
- **Flag:** “or”, “maybe”, “TBD”, alternative designs left side by side, “decide later” on something a later stage needs.
- **Remedy:** Settle the choice in the plan, or cut the work that depends on it.

### 2. Stage atomicity and order

- **Rule:** Each stage is independently shippable. Order is dependency first, then impact among independent stages.
- **Flag:** A stage that cannot be done without a later stage; a stage that mixes unrelated work; “and then everything else”.
- **Remedy:** Split until a stage has one reason to exist; reorder to match real dependencies.

### 3. Checkable acceptance

- **Rule:** Acceptance is something a later agent can pass or fail without inventing a bar. No “it works”.
- **Flag:** Vague done-ness; missing Verify; “implement the feature” as acceptance.
- **Remedy:** Name the files, commands, or observable conditions that mean done.

### 4. Honest scope and assumptions

- **Rule:** Out of scope is real. Assumptions are explicit. Do not smuggle extra work through a stage’s Implementation.
- **Flag:** A stage that quietly expands the goal; implicit platform/tooling assumptions; “also fix X” in the steps.
- **Remedy:** Move the extra work to its own stage or to Out of scope; write the assumption down.

### 5. Feasibility against the current tree

- **Rule:** The plan must be executable against the code that exists now. Wrong layer, ignored helpers, and a path to a god file are plan defects.
- **Flag:** A stage that assumes a module/API that is not there; a plan that ignores an existing canonical helper; a decomposition that will push a file through ~1k lines.
- **Remedy:** Point at the real owner/helper; change the stage so the resulting tree stays healthy.

### 6. Do not launder a bad implementation

- **Rule:** Writing “just add a flag / special case / wrapper” into a plan does not make that design acceptable.
- **Flag:** Planned ad-hoc branches, planned pass-through helpers, planned copies of a helper that already exists.
- **Remedy:** Plan the abstraction or deletion instead; if the messy path is the decision, say so as an explicit, justified exception.

### 7. create-multi-stage-plan stage files

Apply only when the file is a stage under `docs/plans/` with the usual headings.

- **Rule:** `Status`, `Invariants`, and `Acceptance` are present and usable (`pending` / `in_progress` / `blocked` / `done`; invariants that can stay true; acceptance that can be checked).
- **Flag:** Missing `## Status` or a value that is not one of the four; empty or “it works” Acceptance; Invariants that restated the goal.
- **Remedy:** Fix the headings so `implement-pending-plans` can walk the file.

## Primary Review Questions

For every plan directory or stage in scope:

1. Design-judo move that would make the planned result dramatically simpler?
2. Any decision still multi-option or TBD?
3. Are stages atomic and in dependency order?
4. Can Acceptance be checked, or is it “it works”?
5. Is Out of scope honest? Are assumptions written down?
6. Does this fit the current tree (layer, helpers, file size)?
7. Is the plan laundering a bad implementation?
8. What would [code-bar.md](code-bar.md) say about the code this plan would produce?
9. If this is a create-multi-stage-plan stage: are Status / Invariants / Acceptance usable?

## Approval Bar

Do not approve a plan because it is thorough or well-formatted. Approve only when no theme above fires and the would-be implementation would pass [code-bar.md](code-bar.md) (or the misses are explicit, justified exceptions).

**Do not approve** (unless clearly justified) when the plan:

- preserves a visible simpler design
- leaves a decision unset that a later stage needs
- has a non-atomic stage or wrong stage order
- has uncheckable acceptance
- smuggles scope or hides assumptions
- ignores the current tree in a way that will produce a code-bar failure
- plans spaghetti, wrappers, or helper duplication
- is a create-multi-stage-plan stage with unusable Status / Invariants / Acceptance

If any apply, leave explicit actionable feedback and push for the smaller plan.
