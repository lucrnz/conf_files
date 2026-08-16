---
name: implement-pending-plans
description: Implement pending plan stages under docs/plans/. Input: path, basename, field/run, stage path, or retry blocked.
disable-model-invocation: true
---

# Implement pending plans

Input: path, basename, field/run, stage path, or “retry blocked”; else discover under `docs/plans/`.

Selectable plans are directories under `docs/plans/` whose names end in `-pending`. Ignore everything else, including `*-done`. No automatic reopen.

Stages are markdown files under the chosen plan (including nested paths), except `context/`. Do not assume a fixed filename template.

## Plan directory

While any stage still needs work or is `blocked`, leave the directory as `*-pending`. When every stage is `done`, rename by replacing the trailing `-pending` with `-done`. Then, if `context/design.md` exists and does not already start with the archive disclaimer, prepend:

> **Archive.** Decisions in this file were current as of {YYYY-MM-DD} (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

If a `*-pending` plan already has all stages `done` on discovery: archive (this section) and report nothing else to do.

## Status

Under `## Status`, the value is a single trimmed line. Exact literals (case-sensitive): `pending`, `in_progress`, `blocked`, `done`.

Needs work: `pending`, `in_progress`.
Skip: `done`, and `blocked` unless the user asked to retry blocked or named that blocked stage.

Unusable file (missing `## Status`, or value not one of the four): set `blocked` if you can write the file, explain, stop.

## Discover and select

When you list selectable plans, show basename, path, pending/in_progress counts.

1. List selectable plans under `docs/plans/` (or a user-named path).
2. Read each stage file’s Status.
3. A plan is selectable if any stage needs work (`blocked` only when retry applies), or if all stages are `done` (so it can be archived).
4. Selection:
   - Named **stage path**: that stage only (if it needs work or is a retry target); stop after it; archive only if every stage on that plan is then `done`.
   - Named **plan**: A query matches a selectable plan if it equals the path, equals the basename, or equals a hyphen-separated field or a contiguous run of those fields in the basename (`v1stgxr8`, `checkout-rewrite`, `2026-08-16`, `2026-08-16-v1stgxr8`). Exact path or exact basename always wins. Any other query that hits more than one selectable plan asks (questions tool when available). A query that hits none: report no match and list selectable plans. Do not pick.
   - Else one needs-work plan: use it.
   - Several: ask with a list (questions tool when available).
   - None: nothing to do after any all-done archives; stop.

## Walk stages

On the chosen plan, read `context/design.md` if it exists, then order stages sensibly (numbers in names or headings, dependencies in content). Default: every needs-work stage, in order, no pause.

Do not auto-commit, branch, or open PRs.

## Per stage

For each stage that needs work:

1. Set Status to `in_progress`.
2. Implement what the stage asks for (Description, Implementation, Acceptance, and any later sections). Not limited to code — do the work the stage describes.
3. If you cannot finish (underspecified, missing dependency, hard failure, or `## Acceptance` present and not met): set Status to `blocked`, explain to the user, stop the plan (do not continue later stages). Leave the directory as `*-pending`.
4. Otherwise set Status to `done` and continue.

After the walk (or a named stage): if every stage is `done`, archive (Plan directory).

## Summarize

List stages completed this run, any blocked stage and why, any remaining needs-work stages on that plan, and whether the plan directory was renamed to `*-done`. Stop.
