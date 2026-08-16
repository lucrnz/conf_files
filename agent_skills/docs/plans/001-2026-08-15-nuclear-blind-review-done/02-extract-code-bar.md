# Stage 02: Extract code-bar.md

## Status
done

## Description

Move the code review standard out of `nuclear-review/SKILL.md` into `nuclear-review/code-bar.md`. Leave scope workflow, output envelope, and shared tone in `SKILL.md`. Link the bar from `SKILL.md`. Do not change the rules.

## Rationale

Stage 03 adds a second bar. If the code standard is still inline, plan-bar work will either duplicate it or leave SKILL.md as a third home. Extract first, behavior-preserving.

## Invariants

- One home for the code standard: `code-bar.md`.
- In-session `/nuclear-review` still applies the same code bar it does today (this stage is code-only; no plan classification yet).
- Tone, scope resolution, per-scope workflow, and output expectations stay in `SKILL.md`.

## Risks

- A sloppy move drops a theme or the approval checklist. The verify step diffs the moved sections against git history of the pre-extract file.

## Implementation

### Files

- `nuclear-review/code-bar.md` (create)
- `nuclear-review/SKILL.md` (edit)

### Steps

1. Create `nuclear-review/code-bar.md` containing, in order: Review Themes (0–7, each Rule / Flag / Remedy), Primary Review Questions, Approval Bar. Copy the current text; do not rewrite.
2. In `SKILL.md`, replace those three sections with a short pointer: apply [code-bar.md](code-bar.md). Keep Scope, Workflow by Scope, Core Prompt, Review Tone, Output Expectations.
3. Do not add plan language yet.

### Verify

- `git diff` (or a side-by-side against the last commit that still had the sections inline) shows the theme/question/approval text relocated, not rewritten.
- `SKILL.md` contains a relative link to `code-bar.md` and does not restate Rule/Flag/Remedy themes.
- `code-bar.md` still has themes 0–7, the nine primary questions, and the “Do not approve” list.

## Acceptance

- Opening `/nuclear-review` and following `SKILL.md` still reaches the same code standard, via the linked file.
- No rule exists in both files.
