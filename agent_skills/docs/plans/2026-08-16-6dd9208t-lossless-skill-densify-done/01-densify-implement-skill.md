# Stage 01: Densify implement-pending-plans

## Status

done

## Description

Rewrite `implement-pending-plans/SKILL.md` in place so each fact has one home. Same picker, archive, status, walk, and stop behavior. Lift directory lifecycle out of `## Status`.

## Rationale

This file is the larger prompt and the denser restatement cluster (matcher, `*-pending`, archive, order-sensibly). Cutting it first captures most of the token win.

## Invariants

- Matcher semantics unchanged: path, basename, hyphen field or contiguous run; the four examples stay; exact path or exact basename wins; other multi-match asks; zero-match reports and lists selectable plans; do not pick.
- When the skill lists selectable plans, the columns are basename, path, pending/in_progress counts.
- Selectable plans are still only `docs/plans/*-pending`. No reopen of `*-done`.
- Archive still replaces trailing `-pending` with `-done` and prepends the current disclaimer verbatim when `context/design.md` exists and does not already start with it.
- Status values remain the four case-sensitive literals. Needs-work / skip / unusable→`blocked` unchanged.
- Stage files remain “markdown except `context/`”; no required filename template.
- No auto-commit / branch / PR. Blocked still stops the plan. Summarize still ends the run.
- No Python. No other files.

## Risks

A merge that drops “do not pick”, the standalone list-columns sentence, “questions tool when available”, or the disclaimer quote looks shorter and is wrong.

## Implementation

### Files

- `implement-pending-plans/SKILL.md`

### Steps

1. Replace the YAML `description` with exactly:

   `Implement pending plan stages under docs/plans/. Input: path, basename, field/run, stage path, or retry blocked.`

   Leave `name` and `disable-model-invocation` unchanged.

2. Resulting outline (this is the file, not a nest under `## Status`):

   ```
   # Implement pending plans
   lead: input kinds + else discover
   one selectable-plan sentence (ignore non-pending, no reopen)
   one stage-file sentence (markdown except context/; no filename template)

   ## Plan directory
   leave-as-pending / trailing -pending → -done / disclaimer / all-done-on-discovery

   ## Status
   one trimmed line; four literals; needs-work / skip / unusable→blocked

   ## Discover and select
   list-columns sentence
   list / read Status / actionable-this-run
   named stage | named plan (matcher inlined) | one | several | none

   ## Walk stages
   ## Per stage
   ## Summarize
   ```

3. Lead: input kinds only (path, basename, field/run, stage path, or “retry blocked”; else discover under `docs/plans/`). Do not put the matcher here.

4. One selectable sentence: directories under `docs/plans/` whose names end in `-pending`. Ignore everything else, including `*-done`. No automatic reopen. Drop “Companion to…” and “Names come from…”.

5. One stage-file sentence: markdown under the chosen plan (including nested paths), except `context/`. Do not assume a fixed filename template.

6. `## Plan directory` (not under `## Status`): leave-as-`*-pending` while work remains; trailing `-pending` → `-done`; prepend this disclaimer if `context/design.md` exists and does not already start with it (wording must match today’s file, including the `{YYYY-MM-DD}` clause):

   > **Archive.** Decisions in this file were current as of {YYYY-MM-DD} (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

   All-done on discovery: archive (this section) and report nothing else to do.

7. `## Status`: drop the table and the Meaning column. Keep only: one trimmed line under `## Status`; exact literals (case-sensitive) `pending`, `in_progress`, `blocked`, `done`; Needs work = `pending`, `in_progress`; Skip = `done`, and `blocked` unless retry or the named stage is blocked; unusable → set `blocked` if writable, explain, stop. Do not put selectable, archive, or rename here.

8. Immediately under `## Discover and select`, one standalone sentence (the only place that names the columns):

   When you list selectable plans, show basename, path, pending/in_progress counts.

9. Then:
   - List selectable plans under `docs/plans/` (or a user-named path).
   - Read each stage file’s Status.
   - Selectable if any stage needs work (`blocked` only when retry applies), or if all stages are `done` (so it can be archived).
   - Named **stage path**: that stage only (if it needs work or is a retry target); stop after it; archive only if every stage on that plan is then `done`.
   - Named **plan**: this bullet *is* the matcher. Paste the paragraph in step 10 as the body. Do not place it above the dispatch. Do not say “wording may tighten.”
   - Else one needs-work plan: use it. Several: ask with a list (questions tool when available). None: nothing to do after any all-done archives; stop.

   Several-plans and zero-match do not repeat the columns and do not point at each other.

10. Named-plan bullet body, verbatim (do not add the column parenthetical back):

    A query matches a selectable plan if it equals the path, equals the basename, or equals a hyphen-separated field or a contiguous run of those fields in the basename (`v1stgxr8`, `checkout-rewrite`, `2026-08-16`, `2026-08-16-v1stgxr8`). Exact path or exact basename always wins. Any other query that hits more than one selectable plan asks (questions tool when available). A query that hits none: report no match and list selectable plans. Do not pick.

11. Walk: read `context/design.md` if it exists; order stages sensibly (numbers in names or headings, dependencies in content). Default: every needs-work stage, in order, no pause. Do not auto-commit, branch, or open PRs.

12. Per stage and Summarize: keep the current four-step walk and the summary list. After the walk (or a named stage): if every stage is `done`, archive (Plan directory). On `blocked`, leave the directory as `*-pending` and stop the plan.

13. Do not add a mention of any older directory grammar.

### Verify

- `rg -n 'v1stgxr8|checkout-rewrite|2026-08-16-v1stgxr8' implement-pending-plans/SKILL.md` — examples still present, in the named-plan matcher only.
- `rg -n 'Do not pick|do not pick' implement-pending-plans/SKILL.md` — exactly one hit.
- `rg -n 'pending/in_progress counts' implement-pending-plans/SKILL.md` — exactly one hit (the standalone list-columns sentence).
- `rg -n 'same list|match as above|wording may tighten|above or as' implement-pending-plans/SKILL.md` — no hits.
- `rg -n 'Archive\.' implement-pending-plans/SKILL.md` — disclaimer present once, including `the plan date in the directory name`.
- `rg -c 'equals the path' implement-pending-plans/SKILL.md` — matcher body once.
- `rg -n 'Companion to|Names come from' implement-pending-plans/SKILL.md` — no hits.
- `rg -n '^\| Status' implement-pending-plans/SKILL.md` — no table.
- `rg -n '^## Plan directory' implement-pending-plans/SKILL.md` — heading exists.
- `rg -n 'in_progress|blocked' implement-pending-plans/SKILL.md` — all four literals and needs-work/skip still defined.
- `rg -n 'auto-commit' implement-pending-plans/SKILL.md` — still forbidden.
- `wc -w implement-pending-plans/SKILL.md` — report before/after; not a gate.

## Acceptance

- YAML `description` is the sentence in step 1. `disable-model-invocation: true` unchanged.
- Outline matches step 2: `## Plan directory` is not under `## Status`. Status is only literals plus needs-work/skip/unusable.
- Matcher paragraph from step 10 appears once, as the named-plan bullet. No column parenthetical inside it.
- List columns appear once, in the standalone Discover sentence. Several-plans is “ask with a list.”
- `*-pending` / ignore-other / no-reopen stated once. Archive procedure and disclaimer stated once; later steps point at Plan directory.
- An agent following only this file still discovers, selects, walks, blocks, archives, and summarizes as today.
- No file outside `implement-pending-plans/SKILL.md` changed.
