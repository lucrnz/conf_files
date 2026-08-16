> **Archive.** Decisions in this file were current as of 2026-08-16 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# Collision-free plan directory ids

## Goal

Stop allocating a shared incrementing counter when writing `docs/plans/` directories, so two people (or two agents) can create plans in the same repo without racing on `max+1`. New names carry a short minted id. Date is first so minted names `ls`-sort by date. Status stays `-pending` / `-done`.

## Settled decisions

- Directory name: `{YYYY-MM-DD}-{id}-{slug}-pending`. Example: `2026-08-16-v1stgxr8-checkout-rewrite-pending`. Done archives use the same fields with `-done`.
- Date is first so minted names lexicographically sort by date. The mint CLI is the control that stops invented ids, not the field order.
- `{id}` is eight characters from `secrets.choice` over `0123456789abcdefghijklmnopqrstuvwxyz`. No hyphen, no underscore. Hyphen-free so the id is one visible token. No `nanoid`. Runtime dependencies are empty.
- Mint uniqueness is the constructed basename. Retry if `{date}-{id}-{slug}-pending` is already an immediate child of `--plans-dir`. No parse, no id-token set, no “unparsable names contribute no id.”
- Mint tool: `create-multi-stage-plan/scripts/plan-id/` (`cli.py` + `names.py`). Project name `plan-id`, module `plan_id`, same `[tool.uv.build-backend] module-name` override as `blind-review`. uv + pytest + `uv.lock`. CLI is mint-only; prints one basename; does not mkdir.
- `--plans-dir` pointing at a nonexistent directory is an empty name set (exit 0 if the slug is valid). `--date` must match `YYYY-MM-DD`. Retry cap 16, tested.
- implement-pending-plans discovery and archive wording stay as they are (`-pending` / `-done`).
- Picker shows basename, path, and pending/in_progress counts. A query matches a selectable plan if it equals the path, equals the basename, or equals a hyphen-separated field or a contiguous run of those fields in the basename (`v1stgxr8`, `checkout-rewrite`, `2026-08-16`, `2026-08-16-v1stgxr8`). Exact path or exact basename always wins. Any other query that hits more than one selectable plan asks. A query that hits none: report no match and list selectable plans. No `plan-id parse`.
- Frontmatter/input line of implement-pending-plans is updated to the same match keys (path, basename, field/run).
- `nuclear-review` and `select.py` are unchanged.
- This plan and shipped skills state only this write grammar. Verify with positive checks.
- Stage files stay `{stageNN}-{stage-slug}.md`.
- Scope: mint package, implement-pending-plans picker/selection, create-multi-stage-plan write path. No ADR, no rename of existing directories, no extra CLI verbs.

## Design

A shared incrementing counter is a lock. The replacement is a minted 8-character token inside a hyphenated directory name whose last field is still `pending` or `done`. Date leads the name so `ls` on minted directories is chronological.

The id alphabet excludes `-` so the id stays one hyphen-delimited token. Date is `YYYY-MM-DD`; slug is kebab-case; status is `pending` or `done`.

`create-multi-stage-plan` resolves its own skill directory (follow the install symlink) and runs the mint CLI against the target repo’s `docs/plans/`. It never invents an id. If mint fails, it stops and writes nothing.

The mint script validates slug and date, draws an id, and retries if that full basename already exists as an immediate child. It does not parse sibling names. Missing `--plans-dir` on disk is an empty set and is not created.

implement-pending-plans keeps listing `*-pending` and renaming trailing `-pending` to `-done`. Selection uses the picker sentence in Settled decisions. It does not invoke `plan-id`.

Slug is kebab-case `[a-z0-9]+(-[a-z0-9]+)*`. The mint CLI rejects any other slug.

## Stage map

Mint first so the basename is tested before any skill quotes the invoke line. implement-pending-plans picker next so selection language matches basenames and hyphen-fields before the writer emits them. Create skill last: that is the write switch.

## Out of scope

- Renaming any existing `docs/plans/` directory
- Changing `{stageNN}-{stage-slug}.md`
- Editing `nuclear-review` or `select.py`
- An ADR
- `list` / `parse` / `resolve` CLI commands
- `mkdir` inside the mint tool
- Windows as a runtime support bar for the agent
- Repo-wide uniqueness of the 8-character id across different dates

## Assumptions

- Sibling uv layout is the template: `requires-python >= 3.11`, `uv_build`, `[project.scripts]`, pytest in the dev group, committed `uv.lock`.
- Id bytes come from `secrets`; no PyPI runtime dependency.
- Target `docs/plans/` is cwd-relative unless `--plans-dir` is absolute. The create skill always passes `--plans-dir docs/plans`.
- Two concurrent mints can theoretically print the same unused basename before either directory exists; retry-on-existing plus 8-char draws makes that acceptable.
- Archive disclaimer still uses “the plan date in the directory name” (the leading `YYYY-MM-DD`).
