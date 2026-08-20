---
name: archive-done-plans
description: Git-rm done docs/plans/*-done directories and index them in ARCHIVED.md. Input: path, basename, or field/run; else multi-select. Use when the user runs /archive-done-plans.
disable-model-invocation: true
---

# Archive done plans

Input: path, basename, field/run; else discover under `docs/plans/`. Git only: `git rev-parse --is-inside-work-tree` fails → stop.

Selectable plans are immediate children of `docs/plans/` whose names end in `-done`. Ignore `*-pending` and `ARCHIVED.md`. No rename. No reopen. Do not write stage files. Stage files follow implement-pending-plans.

## Eligible

A listed `*-done` dir is selectable only if (a) every stage file’s `## Status` is exactly `done` and (b) every path under that directory is tracked and `git status --porcelain` for that directory is empty. Unusable Status (missing heading or value not one of implement-pending-plans’ four) makes the directory ineligible. Ineligible: report why, omit from the selectable list.

If `docs/plans/ARCHIVED.md` exists, it must be tracked and clean before a run that will edit it; otherwise stop. Other dirty files are fine. Stage only the paths this skill names.

## Discover and select

When you list selectable plans, show basename and path.

1. List `*-done` children of `docs/plans/`.
2. Drop ineligible directories (Eligible).
3. Selection:
   - Named **plan**: implement-pending-plans’ named-plan match keys against this selectable set. Exact path or exact basename always wins (that one plan; no ask). Several hits → ask over **those hits**. None → report no match and list selectable; do not pick.
   - Else one selectable → use it.
   - Several → ask over **all selectable**.
   - None → stop.

Ask (when Selection says ask): questions tool, `multi_select`. Option 1 is **Archive all** — the whole listed set (the set the ask is over), not a directory. Then one option per listed plan (basename and path). Empty or declined picker → stop. If Archive all is among the ticks, the selected set is the whole listed set. Otherwise the selected set is the ticked plans.

After a selected set exists: sort it by basename. For each plan in that order: Recap, Commit 1, Commit 2. If Commit 2 fails: report that plan’s commit-1 SHA, do not `git reset`, do not start later selected plans, then Summarize what finished and stop.

## Recap

Read `context/design.md` if present and stage titles. Write 2–3 sentences: what shipped, and why a later agent would open the diff. Title = first ATX H1 in `design.md`; if missing, basename. Do not copy Settled decisions. Do not list stage files.

## Commit 1

Two commits: `git rm` first, then the index. A commit cannot contain its own hash; record the SHA after this commit. SHA never appears in either commit subject or body.

`git rm -r` the plan directory. Stage only those deletions. Subject from Sniff (`archive {slug}`). Commit. Record `git rev-parse HEAD` (full 40-char SHA).

## Commit 2

If `docs/plans/ARCHIVED.md` does not exist, create it with exactly this intro and nothing else yet:

```markdown
# Archived plans

Done plan directories removed from `docs/plans/` via git rm. Each entry's command shows that plan's delete commit.
```

Append one section (do not prepend; oldest first). Do not rewrite the intro. Do not reorder existing entries. Leading blank line so it does not run into the previous block:

````markdown
## {basename}

**Title:** {title}

**Commit:** `{sha}`

{recap}

```bash
git show {sha}
```
````

Stage only `docs/plans/ARCHIVED.md`. Subject from Sniff (`index archived plan {slug}`). If this commit fails: report the commit-1 SHA, do not `git reset`, stop.

## Sniff

`git log -15 --format=%s` (or fewer if the repo is shorter). Conventional = `^(feat|fix|docs|chore|refactor|test|style|perf|ci|build)(\([^)]+\))?: `. If a majority of those subjects match: type `docs`; scope = the most common parenthetical scope among the conventional ones, omitted on a tie or if none have a scope. Subjects: `docs(<scope>): archive {slug}` / `docs(<scope>): index archived plan {slug}`, or the same without `(<scope>)`. If not a conventional majority: `docs: archive {slug}` and `docs: index archived plan {slug}`.

`{slug}` is the plan-slug field of create-multi-stage-plan’s `{YYYY-MM-DD}-{id}-{slug}-done` name. If the basename does not match `^[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9a-z]{8}-(.+)-done$`, `{slug}` is the basename.

## Summarize

For each plan this run archived, or whose rm committed before a failed index: basename, both subjects, the SHA, the `git show` command, and whether `ARCHIVED.md` was created or appended. Stop.
