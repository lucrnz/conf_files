# Stage 01: archive-done-plans skill

## Status
done

## Description

Add `archive-done-plans/SKILL.md` as a git-only agent procedure that pickers one eligible `docs/plans/*-done` directory, `git rm`s it in its own commit, then appends `docs/plans/ARCHIVED.md` with a recap and `git show` of that commit. Symlink the new skill per `README.md`.

## Rationale

This is the only artifact. The complementary skills stay untouched; the procedure has to live in one file so selection, gates, and the two-commit index cannot drift.

## Invariants

- `implement-pending-plans/SKILL.md` and `create-multi-stage-plan/SKILL.md` are not modified.
- No `archive-done-plans/scripts/` (or any other file under that directory except `SKILL.md`).
- Frontmatter: `name: archive-done-plans`, `disable-model-invocation: true`, and a description that names `docs/plans/`, `*-done`, `ARCHIVED.md`, input kinds (path, basename, field/run), and `/archive-done-plans`.
- Named-plan match keys are a pointer to implement-pending-plans’ named-plan bullet. Do not copy that paragraph or its examples.
- Status literals are not re-listed. Eligibility says every stage Status must be the literal `done`; unusable Status (missing heading or value not one of implement’s four) makes the directory ineligible. This skill does not write stage files.
- Write-grammar slug parse is a pointer to create-multi-stage-plan’s `{YYYY-MM-DD}-{id}-{slug}-done` name plus the fallback: if the basename does not match `^[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9a-z]{8}-(.+)-done$`, `{slug}` is the basename.
- SHA appears only in `ARCHIVED.md`. Neither commit subject nor body includes a hash.
- New index sections are appended (oldest first). Existing intro and entries are not rewritten or reordered.

## Risks

- A later agent will try to put the SHA in the rm commit or amend it in. The skill needs one sentence that a commit cannot contain its own hash, then the two-commit order.
- Oldest-first is easy to invert. The skill must say append, not prepend.
- Sniffing scope from this repo’s `docs(agent_skills):` history must stay a general majority-scope rule, not a hard-coded `agent_skills` string.

## Implementation

### Files

- `archive-done-plans/SKILL.md`

### Steps

1. Create `archive-done-plans/SKILL.md` only. Follow `skill-design-principles` (one home per fact, no no-op sprawl). Dense like `implement-pending-plans/SKILL.md`.

2. Body, in this order (extra headings only after these):

   **Lead.** Input: path, basename, field/run; else discover under `docs/plans/`. Works only on git; `git rev-parse --is-inside-work-tree` fails → stop.

   **Selectable set.** Immediate children of `docs/plans/` whose names end in `-done`. Ignore `*-pending` and `ARCHIVED.md`. No rename. No reopen.

   **Eligible.** A listed `*-done` dir is selectable only if (a) every stage file (markdown under the plan except `context/`, same rule as implement-pending-plans) has `## Status` exactly `done`, and (b) every path under that directory is tracked and `git status --porcelain` for that directory is empty. Ineligible: report why, omit from the selectable list. `ARCHIVED.md`, if it exists, must be tracked and clean before a run that will edit it; otherwise stop.

   **Discover and select.** List selectable plans as basename and path. Named plan: implement-pending-plans’ named-plan match keys against this selectable set; exact path or exact basename always wins; several hits → ask (questions tool when available); none → report no match and list selectable; do not pick. Else one selectable → use it. Several → ask. None → stop. One plan per run.

   **Recap.** Read `context/design.md` if present and stage titles. Write 2–3 sentences: what shipped, and why a later agent would open the diff. Title = first ATX H1 in `design.md`; if missing, basename. Do not copy Settled decisions. Do not list stage files.

   **Commit 1.** `git rm -r` the plan directory. Stage only those deletions. Subject from the sniff rule below (`archive {slug}`). Commit. Record `git rev-parse HEAD` (full 40-char SHA).

   **Commit 2.** If `docs/plans/ARCHIVED.md` does not exist, create it with exactly this intro and nothing else yet:

   ```markdown
   # Archived plans

   Done plan directories removed from `docs/plans/` via git rm. Each entry's command shows that plan's delete commit.
   ```

   Append one section (leading blank line so it does not run into the previous block):

   ```markdown
   ## {basename}

   **Title:** {title}

   **Commit:** `{sha}`

   {recap}

   ```bash
   git show {sha}
   ```
   ```

   Stage only `docs/plans/ARCHIVED.md`. Subject from the sniff rule (`index archived plan {slug}`). If this commit fails: report the commit-1 SHA, do not `git reset`, stop.

   **Sniff.** `git log -15 --format=%s` (or fewer if the repo is shorter). Conventional = `^(feat|fix|docs|chore|refactor|test|style|perf|ci|build)(\([^)]+\))?: `. If a majority of those subjects match: type `docs`; scope = the most common parenthetical scope among the conventional ones, omitted on a tie or if none have a scope. Subjects: `docs(<scope>): archive {slug}` / `docs(<scope>): index archived plan {slug}`, or the same without `(<scope>)`. If not a conventional majority: `docs: archive {slug}` and `docs: index archived plan {slug}`.

   **Summarize.** Basename, both subjects, the SHA, the `git show` command, and whether `ARCHIVED.md` was created or appended. Stop.

3. Install: `ln -sfn` this repo’s `archive-done-plans` into `~/.agents/skills/archive-done-plans` as in `README.md`.

4. Do not run the new skill against existing `*-done` directories in this repo.

### Verify

- `test -f archive-done-plans/SKILL.md`
- `git diff -- implement-pending-plans/SKILL.md create-multi-stage-plan/SKILL.md` is empty
- Frontmatter contains `name: archive-done-plans` and `disable-model-invocation: true`
- Body contains `ARCHIVED.md`, `git rm`, two-commit order, `git show`, `append`, and a pointer to implement-pending-plans for match keys
- Body does not contain the implement-pending-plans example tokens `v1stgxr8` or `checkout-rewrite`
- `ls -l ~/.agents/skills/archive-done-plans` is a symlink to this repo’s `archive-done-plans`
- No `archive-done-plans/scripts/` directory

## Acceptance

- `archive-done-plans/SKILL.md` exists and is the only file added under that directory.
- implement-pending-plans and create-multi-stage-plan are byte-identical to HEAD.
- An agent following the file would refuse a non-git cwd, refuse a `*-done` dir with a non-`done` stage, ask when several eligible dirs exist, create two commits per successful archive, put the SHA only in `ARCHIVED.md`, and append (not prepend) the new section.
- The skill is reachable as `~/.agents/skills/archive-done-plans`.
