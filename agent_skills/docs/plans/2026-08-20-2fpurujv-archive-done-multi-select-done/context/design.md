> **Archive.** Decisions in this file were current as of 2026-08-20 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# Multi-select for archive-done-plans

## Goal

Change `archive-done-plans` so a picker that would have asked for one plan is a multi-select, and the run archives every selected eligible `*-done` directory.

## Settled decisions

- Same skill: `archive-done-plans/SKILL.md` only. Not a new skill. Do not edit implement-pending-plans or create-multi-stage-plan.
- Eligibility, git gates, two-commit archive, `ARCHIVED.md` shape, sniff, recap, and match-key pointer stay as they are.
- Exact path or exact basename still wins and skips the ask. One eligible still auto-takes. None / no match still stop. Empty or declined picker → stop.
- When the agent would ask (bare invoke with several eligible, or a named query that hits several): questions-tool multi-select. The option list is the set being asked about (all eligible, or only those named-query hits).
- First option is **Archive all** (the whole listed set). Remaining options are the listed plans (basename and path). If Archive all is ticked with anything else, the selected set is the whole listed set. Otherwise the selected set is the ticked plans.
- Process the selected set in basename order. Each plan still gets its own rm commit plus index commit.
- If an index commit fails: report that plan’s rm SHA, do not `git reset`, do not start the next selected plan.
- Summarize every plan this run touched (same fields as today, once per plan).

## Design

The skill already builds a listed set and then asks when that set has more than one member. The ask becomes multi-select over that same set. Archive all is a listed-set operator, not a plan: it is the first option so it is visible, and it wins whenever it is ticked so a mixed tick cannot mean “all plus a subset.”

Basename sort after selection keeps `ARCHIVED.md` oldest-first regardless of checkbox order. The per-plan procedure is unchanged; the new work is the selected set, the sort, and stopping the rest of the batch on the same index-commit failure that already stops a single-plan run.

## Stage map

One stage: selection, Archive all, the batch loop, and summarize must change together in the one file that owns them.

## Out of scope

- A new skill or a rename of `archive-done-plans`
- Edits to implement-pending-plans or create-multi-stage-plan
- Changing eligibility, two-commit SHA rules, `ARCHIVED.md` entry format, or sniff
- A helper script
- Running the skill against this repo’s `*-done` directories as part of implementing this plan

## Assumptions

- The questions tool supports `multi_select`.
- After a successful pair of commits, `ARCHIVED.md` is clean again for the next plan in the batch.
