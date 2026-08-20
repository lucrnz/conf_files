# Stage 01: multi-select picker and batch

## Status
done

## Description

Rewrite the Discover and select (and Summarize) parts of `archive-done-plans/SKILL.md` so asks are multi-select, Archive all is the first option and wins if ticked, and the run archives the selected set in basename order, stopping the batch on an index-commit failure.

## Rationale

The rest of the skill already knows how to archive one plan. The defect is the ask (one choice) and the “one plan per run” stop. Those two sentences have to change in the same file as the loop that follows them.

## Invariants

- Only `archive-done-plans/SKILL.md` changes.
- implement-pending-plans and create-multi-stage-plan are untouched.
- Eligible, Recap, Commit 1, Commit 2, and Sniff keep their current contracts (two commits per plan, SHA only in `ARCHIVED.md`, append, hash sentence, sniff regex).
- Named-plan match keys remain a pointer to implement-pending-plans. Do not copy that paragraph or its examples (`v1stgxr8`, `checkout-rewrite`).
- No `scripts/` under `archive-done-plans/`.

## Risks

- An agent treats “Archive all” as a directory name. The skill must say it is the listed set, first option, and that a mixed tick with Archive all means the whole listed set.
- An agent archives in checkbox order. The skill must say sort selected basenames before the first `git rm`.
- An agent continues the batch after a failed index commit. The skill must say stop the batch (same no-`git reset` rule as today).

## Implementation

### Files

- `archive-done-plans/SKILL.md`

### Steps

1. Follow `skill-design-principles`. Do not restate Recap / Commit 1 / Commit 2 / Sniff. Point the batch at those headings.

2. Delete “One plan per run.”

3. Discover and select — keep list columns (basename and path) and the numbered discover steps. Replace the Selection arms with:
   - Named **plan**: implement-pending-plans’ named-plan match keys against this selectable set. Exact path or exact basename always wins (that one plan; no ask). Several hits → ask over **those hits**. None → report no match and list selectable; do not pick.
   - Else one selectable → use it.
   - Several → ask over **all selectable**.
   - None → stop.

4. Ask (when the arms above say ask): questions tool, `multi_select`. Option 1 is **Archive all** — the whole listed set (the set the ask is over). Then one option per listed plan (basename and path). Empty or declined picker → stop. If Archive all is among the ticks, the selected set is the whole listed set. Otherwise the selected set is the ticked plans.

5. After a selected set exists: sort it by basename. For each plan in that order: Recap, Commit 1, Commit 2. If Commit 2 fails: report that plan’s commit-1 SHA, do not `git reset`, do not start later selected plans, then Summarize what finished and stop.

6. Summarize: for each plan this run archived (or whose rm committed before a failed index), the current fields (basename, both subjects, SHA, `git show`, created vs appended). Stop.

7. Frontmatter description may mention multi-select; it must still name `docs/plans/`, `*-done`, `ARCHIVED.md`, path/basename/field/run, and `/archive-done-plans`.

### Verify

- `git diff -- implement-pending-plans/SKILL.md create-multi-stage-plan/SKILL.md` is empty
- `archive-done-plans/SKILL.md` does not contain `One plan per run`
- Body contains `multi_select` or `multi-select`, `Archive all`, and `basename` as the batch order
- Body still contains `ARCHIVED.md`, `git rm`, `git show`, `append`, and a pointer to implement-pending-plans for match keys
- Body does not contain `v1stgxr8` or `checkout-rewrite`
- No `archive-done-plans/scripts/`

## Acceptance

- An agent following the file would, given four eligible `*-done` dirs and no name, open a multi-select whose first option is Archive all.
- Ticking Archive all plus one plan archives all four, in basename order, two commits each.
- Ticking two plan options (no Archive all) archives only those two, still basename-sorted.
- A field/run query that hits two plans asks only over those two (Archive all = those two).
- Exact basename still archives that one plan with no ask.
- A failed index commit stops the batch and leaves later selected dirs on disk.
- implement-pending-plans and create-multi-stage-plan are byte-identical to HEAD.
