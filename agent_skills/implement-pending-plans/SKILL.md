---
name: implement-pending-plans
description: Implement pending plan stages under docs/plans/; walk one *-pending plan in order; skip context/; Status in_progress → done/blocked; no auto git.
disable-model-invocation: true
---

# Implement pending plans

Input: optional plan id, stage path, or “retry blocked”; else discover under `docs/plans/`.

Companion to `create-multi-stage-plan`. Plans are directories under `docs/plans/` whose names end in `-pending`.

**Stages:** markdown files under the chosen plan (including nested paths), except anything under `context/`. Do **not** assume a fixed stage filename template; order them sensibly.

Ignore directories under `docs/plans/` that do not end in `-pending` (including `*-done` and anything else). No automatic reopen of finished plans.

## Status

### Plan directory

- Selectable plans: directory names ending in `-pending`.
- While any stage still needs work (or is blocked), leave the directory as `*-pending`.
- When every stage file is `done`, rename by replacing the trailing `-pending` with `-done`. Then, if `context/design.md` exists and does not already start with the archive disclaimer, prepend:

  > **Archive.** Decisions in this file were current as of {YYYY-MM-DD} (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

- If a `*-pending` plan already has all stages `done` on discovery: rename to `*-done` (and stamp `context/design.md` as above) and report nothing else to do.

### Stage files

Under `## Status`, the value is a single trimmed line. Exact literals (case-sensitive):

| Status | Meaning |
|--------|---------|
| `pending` | Not started |
| `in_progress` | Started, not finished |
| `blocked` | Cannot finish; needs human input or fix |
| `done` | Finished |

**Needs work:** `pending`, `in_progress`.  
**Skip:** `done`, and `blocked` unless the user asked to retry blocked (or named that blocked stage).

Unusable file (missing `## Status`, or value not one of the four): set `blocked` if you can write the file, explain, stop.

## 1. Discover and select

1. List `*-pending` plan directories under `docs/plans/` (or under a user-named path).
2. Under each plan directory, find stage files and read each file’s Status.
3. A plan is selectable if it has any stage that needs work (include `blocked` only when retry applies), or if all stages are already `done` (so you can rename — see Plan directory above).
4. Selection:
   - User named a **stage path**: that stage only (if it needs work or is a retry target); then stop after it. Do not rename the plan directory unless every stage on that plan is `done` after the run.
   - User named a **plan** (id, slug, or path): that plan.
   - Else if exactly one selectable plan with needs-work stages: use it.
   - Else if several: ask with a list (questions tool when available); show planNNN, slug, path, and pending/in_progress counts.
   - Else: report nothing to do (after any all-done renames), stop.

## 2. Walk stages

On the chosen plan, read `context/design.md` if it exists, then order stages sensibly (e.g. numbers in names or headings, dependencies in content). No required filename grammar.

Default: every stage that needs work, in order, without pausing between stages.

Do **not** auto-commit, branch, or open PRs.

## 3. Per stage

For each stage that needs work:

1. Set Status to `in_progress`.
2. Implement what the stage asks for (Description, Implementation, Acceptance, and any later sections). Not limited to code — do the work the stage describes.
3. If you cannot finish (underspecified, missing dependency, hard failure, or `## Acceptance` present and not met): set Status to `blocked`, explain to the user, **stop the plan** (do not continue later stages). Leave the plan directory as `*-pending`.
4. Otherwise set Status to `done` and continue.

After the walk (or after a single named stage): if every stage on the plan is `done`, rename `*-pending` → `*-done` (see Plan directory).

## 4. Summarize

List stages completed this run, any blocked stage and why, any remaining needs-work stages on that plan, and whether the plan directory was renamed to `*-done`. Stop.
