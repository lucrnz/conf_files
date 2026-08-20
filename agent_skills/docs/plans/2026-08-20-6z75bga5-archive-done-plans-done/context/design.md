> **Archive.** Decisions in this file were current as of 2026-08-20 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# Archive done plans

## Goal

Add an `archive-done-plans` skill that, in a git repo, removes one finished `docs/plans/*-done` directory with `git rm` and indexes it in `docs/plans/ARCHIVED.md`. Agents recover the plan with `git show <sha>` instead of keeping the tree on disk.

## Settled decisions

- Complementary only: consume directories already named `*-done`. Do not rename, do not chain from implement-pending-plans, and do not edit that skill or create-multi-stage-plan.
- Git only. Not a git repo → stop.
- One plan per run. Selection is a picker over eligible `*-done` dirs: named path / basename / field-or-run uses implement-pending-plans’ named-plan match keys; exact path or exact basename always wins; one eligible → take it; several → ask; none → stop. List columns are basename and path only.
- A `*-done` directory is ineligible if any stage Status is not the literal `done` (including missing or unusable Status), or if the directory is not fully tracked and clean. Report ineligible dirs; do not list them as selectable. Continue discovery.
- Surgical staging. Other dirty files are fine. The plan directory and `docs/plans/ARCHIVED.md` (if it exists) must be clean before the run. Untracked or partially tracked plan dir → refuse that plan.
- Two commits. Commit 1 is `git rm` of the plan directory only. Commit 2 appends the `ARCHIVED.md` entry that stores commit 1’s full SHA and `git show <sha>`. A commit cannot contain its own hash; the SHA never appears in either commit message.
- If commit 2 fails after commit 1: report the rm SHA and stop. Do not `git reset` the rm.
- `docs/plans/ARCHIVED.md` is the only index. Create it with a short stable intro if missing; never rewrite that intro; never reorder existing entries. New `## {basename}` sections are appended (oldest first).
- Recap is agent-written, 2–3 sentences: what shipped, and why a later agent would open the diff. Not a Settled-decisions dump and not a stage file listing. Title is the first ATX H1 in `context/design.md` (the Archive disclaimer is a blockquote, not the title). No design.md or no H1 → title is the basename.
- Commit subjects: sniff `git log -15 --format=%s`. If a majority of those subjects are conventional (`type` or `type(scope):`), use `docs` and the dominant scope when one exists: `docs(<scope>): archive {slug}` and `docs(<scope>): index archived plan {slug}`; otherwise `docs: archive {slug}` and `docs: index archived plan {slug}`. Absolute fallback is the no-scope pair. `{slug}` is the plan-slug field of the write grammar; if the basename does not match, use the basename.
- Form: `archive-done-plans/SKILL.md` only. No helper script. `disable-model-invocation: true`.
- Match keys and Status literals stay owned by implement-pending-plans. Write grammar `{YYYY-MM-DD}-{id}-{slug}-pending|done` stays owned by create-multi-stage-plan. This skill points; it does not restate those paragraphs.

## Design

implement-pending-plans leaves `*-done` trees in `docs/plans/` and already calls that step “archive.” This skill is the next, optional, git-only step: drop a finished tree from the working copy and keep a thin index so a later agent can still open it.

The index cannot live in the rm commit if it must cite that commit’s SHA. Commit 1 is therefore a pure deletion. `git rev-parse HEAD` after that commit is the hash stored in `ARCHIVED.md`. Commit 2 is only the index update. `git show <sha>` on commit 1 is the archive diff (every file in the plan, as a deletion).

Eligibility is a read of the candidate directory, not a rename. Stage files are not edited. `*-pending` is invisible. A dirty or untracked plan is refused because `git rm` would not produce a recoverable snapshot of what is on disk.

Commit-subject detection is a procedure on the target repo’s recent history, not a hard-coded `agent_skills` scope. The fallback is conventional `docs:`.

The skill is an agent procedure in the same family as implement-pending-plans: one `SKILL.md`, no CLI. Install is this repo’s existing symlink loop.

## Stage map

One stage: the only repo artifact is `archive-done-plans/SKILL.md`. Selection, git gates, two-commit archive, and index format are one procedure and must be written together so they cannot drift. The install symlink is the last step of that stage, not its own stage.

## Out of scope

- Edits to `implement-pending-plans` or `create-multi-stage-plan`
- A helper script or `scripts/` tree
- Running the new skill against this repo’s existing `*-done` directories as part of implementing this plan
- Changes to `nuclear-review`, `plan-id`, or `README.md`
- An ADR
- Storing a commit’s own SHA inside that same commit, or `git commit --amend` to plant a hash
- Windows as a runtime support bar

## Assumptions

- Target layout is the same `docs/plans/` the sibling plan skills already hardcode.
- Questions tool is used when several eligible `*-done` directories exist.
- `uv` is not required to run this skill.
- Per-skill install remains `ln -sfn` into `~/.agents/skills/` as in `README.md`.
