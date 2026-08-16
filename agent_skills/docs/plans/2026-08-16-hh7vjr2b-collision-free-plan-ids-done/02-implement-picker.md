# Stage 02: implement-pending-plans picker

## Status
done

## Description

Update `implement-pending-plans/SKILL.md` selection, picker, and the input line so they all use the same match sentence. Discovery and archive stay exactly as they are.

## Rationale

Minted names are `{date}-{id}-{slug}-pending`. Showing the whole basename needs no parser. Matching a hyphen-separated field or a contiguous run of fields lets a user type `v1stgxr8` or `checkout-rewrite` without a second grammar home.

## Invariants

- Discovery, selectable-suffix, and archive-rename paragraphs are unchanged.
- implement-pending-plans does not invoke `plan-id`.
- One match sentence, used for the input line, named-plan rule, and picker: a query matches a selectable plan if it equals the path, equals the basename, or equals a hyphen-separated field or a contiguous run of those fields in the basename (`v1stgxr8`, `checkout-rewrite`, `2026-08-16`, `2026-08-16-v1stgxr8`). Exact path or exact basename always wins. Any other query that hits more than one selectable plan asks. A query that hits none: report no match and list selectable plans.
- Several-plans picker: basename, path, pending/in_progress counts. No per-field columns.
- The write template is not restated here. One sentence may say names come from `create-multi-stage-plan`.

## Risks

- Embedding a mint regex, or listing date/id/slug as picker columns, recreates a parser the skill must not own. Keep the match sentence above; do not add a second wording.
- Editing the discovery/archive bullets in passing can drift them. Touch selection, picker, and the input line only.

## Implementation

### Files

- `implement-pending-plans/SKILL.md`

### Steps

1. Keep section “Discover and select” listing `*-pending` as today.
2. Change the input/frontmatter line so it names path, basename, or field/run — not a bare “plan id” with no definition.
3. Under “User named a **plan**”: paste the match sentence from Invariants (same words). Questions tool when asking on multi-match.
4. Several-plans list: show basename, path, and pending/in_progress counts.
5. Zero-match: report no match and list selectable plans (same columns). Do not pick.
6. Leave Status, walk, per-stage, and summarize sections alone.
7. Do not add a `uv run` / `plan-id` line.

### Verify

- The input line, the named-plan sentence, and any restatement of matching use the same match sentence as Invariants (path, basename, hyphen-separated field or contiguous run; exact path/basename wins; other multi-match asks; zero-match reports and lists).
- The picker sentence lists basename, path, and pending/in_progress counts, and does not list date, id, or slug as columns.
- Discovery still says list `*-pending`; archive still replaces trailing `-pending` with `-done`.
- The file does not contain a `plan-id` invoke line.
- `create-multi-stage-plan/SKILL.md` is untouched.

## Acceptance

- The input line, the named-plan sentence, and any restatement of matching use the same match sentence as Invariants (path, basename, hyphen-separated field or contiguous run; exact path/basename wins; other multi-match asks; zero-match reports and lists).
- The picker sentence lists basename, path, and pending/in_progress counts, and does not list date, id, or slug as columns.
- Discovery still says list `*-pending`; archive still replaces trailing `-pending` with `-done`.
- The file does not contain a `plan-id` invoke line.
