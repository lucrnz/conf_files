**Archive.** Decisions in this file were current as of 2026-08-21 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# Construction contracts

## Goal

Prompt-only edits so a stage’s `## Files` is a closed, matchable path contract, nuclear plan review fails on a broken Files list instead of looping on speculative judo, and implement cannot invent a path outside that list.

## Settled decisions

- Touch only `create-multi-stage-plan`, `plan-bar.md`, and `implement-pending-plans`. No new skill, no CLI, no grilling rewrite, no code-bar rewrite, no nuclear-review workflow coupling.
- Construction artifact is Files only. Stage map stays dependencies and order — not owners, not a file listing. `design.md` still has no Implementation, file lists, or Acceptance.
- A Files entry is either an exact repo-relative file path, or a directory prefix that ends with `/`. Prefix match is slash-bounded. Empty, `.`, and `/` are illegal prefixes. A prefix must contain at least one path segment.
- Every repo path named in that stage’s Steps must appear as an exact Files entry. `None` is legal only when Steps name no path. A prefix does not satisfy that write-time rule; it only authorizes later growth.
- Implement reads **this stage’s** Files only. After `in_progress`, before work: path already listed → continue; path under a listed prefix → append the exact path to this stage’s Files, continue, report; otherwise `blocked`, stop later stages. Implement may not add a prefix. Parent directories of a listed file do not need their own entry.
- Plan-bar still asks for design judo. A construction-complete plan (Files contract held, no planned ~1k growth, no laundering) must not be refused solely for a hypothetical simpler product model. Theme 7 owns the Files contract (cite create-multi-stage-plan). Theme 5 keeps planned ~1k. Construction folds into primary question 9. No ninth theme.
- No living-plan machinery: no findings stages, no archive-waits-for-nuclear, no product-vs-construction amend matrix, no re-lint rules.

## Design

One Files contract, three verbs.

`create-multi-stage-plan` is the source of truth for the contract shape (what a Files entry is, what `None` means, that a Steps/Files mismatch is still multi-option). `plan-bar.md` and `implement-pending-plans` point at that skill; they do not restate the entry grammar or the match algorithm.

Write-time: refuse to emit a plan directory while any stage’s Steps name a path that is not an exact Files entry, or while Files contains an illegal prefix. Same class of block as leftover product forks.

Review-time: fail those same holes via theme 7. Fail planned ~1k via theme 5 (already there). Keep theme 0 as a question. Change only the approval bar so “preserves a visible simpler design” is not a solo refuse when Files, ~1k, and no-laundering are clean.

Implement-time: this stage’s Files is the path set. Growth is allowed only under a prefix that stage already listed. A new prefix is off-plan (`blocked`).

Edits stay short. Add or change the few sentences that implement the verbs. Do not add worked examples, cycle essays, or living-plan negations.

## Stage map

1. **Write-time contract** — defines the Files grammar and the refuse-to-write rule in `create-multi-stage-plan`. Later stages have nothing to point at until this exists.
2. **Review-time lint** — depends on that vocabulary. Highest impact on the review-loop pain once the contract exists.
3. **Implement-time obedience** — depends on the write-time vocabulary only. Independent of stage 02; shipped after so review and implement agree on the same contract in one plan.

## Out of scope

- `grilling`, `grill-me`, `grill-with-docs`
- `nuclear-review/SKILL.md`, `code-bar.md`, `nuclear-blind-review`
- Auto-running nuclear review, findings stages, archive policy changes
- New skills, scripts, or tests beyond reading the three markdown files
- Encoding the full living-plan advice from the earlier grilling session
- Stage map owners, `## Owner` headings, plan-wide Files unions

## Assumptions

- Skill-design-principles apply: one home per fact, no no-op guardrails, no restated contract in three files.
- Existing plan-bar themes 1, 5, 6, and 7 already cover forks, ~1k-via-tree, laundering, and stage headings. This plan extends theme 7 and the approval bar; it does not mint a parallel bar.
- `implement-pending-plans` already blocks on underspecified. A path outside this stage’s Files is that path, not a new status value.
