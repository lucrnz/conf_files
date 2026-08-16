---
name: nuclear-review
description: Extremely strict maintainability review of code and of docs/plans/ (abstraction quality, giant files, spaghetti growth, plan judo). Triggers: nuclear review, deep code quality audit, harsh maintainability review. Use when the user runs /nuclear-review. Default scope=changes; also scope=codebase or scope=picker / picker for an inclusive commit range.
disable-model-invocation: true
---

# Nuclear Review

Unusually strict review of implementation quality, maintainability, abstraction quality, and codebase health.

**Above all:** be ambitious about structure. Do not stop at local cleanup. Hunt **code judo** — behavior-preserving restructures that make the implementation dramatically simpler. Prefer **deleting** complexity over rearranging it.

## Scope

| Argument | Values | Default |
| --- | --- | --- |
| `scope` | `changes` \| `codebase` \| `picker` | `changes` |

Resolve before reviewing:

1. `picker` / `picker=true` / `scope=picker` / interactive commit-range language → `scope=picker`.
2. Full-repo / entire-codebase / whole-application audit → `scope=codebase`.
3. Current changes, working tree, staged/unstaged diff, or unspecified → `scope=changes`.
4. Picker/range language mixed with full-repo/`codebase` language → **stop and ask** which scope. Do not guess.
5. When in doubt → `changes`.

Examples: `nuclear review` → `changes`; `… scope=codebase` → `codebase`; `… picker` → `picker`.

## Workflow by Scope

### `scope=changes` (default)

Working-tree review (no PR/feature branch required).

1. `git status --short` — modified, staged, deleted, untracked.
2. `git diff` and `git diff --cached`.
3. Read relevant untracked files directly.
4. Review surface = staged ∪ unstaged ∪ relevant untracked.
5. Large files: enough surrounding context to judge decomposition; findings stay anchored to what this change set introduced or failed to fix.

Focus:

- Did this change set make the area simpler or messier? Push past 1k lines or add spaghetti?
- Code-judo move within/adjacent to this diff — or did the author stop at “move the big function” instead of deleting complexity?

### `scope=picker`

Interactive inclusive commit range, reviewed as one change set.

1. Candidates: `git log -n 30 --format='%h %s' HEAD` (full history, not `--first-parent`), newest first. Labels: `short hash + subject`.
2. No usable history → explain and **stop**. No invented range, no scope fallback.
3. Dirty worktree → warn in preamble; **do not** include uncommitted work.
4. Pick **start S**, then **end E**:
   - Questions tool if available; else print numbered options and **stop** until answered. Do not guess.
   - Q1: S from the candidate list.
   - Q2: E from candidates that are S or descendants of S (`git merge-base --is-ancestor S E`). **No recommended default** for E.
   - `S == E` allowed (single-commit review).
5. Inclusive range (S and E both included):
   - S has parent → `git diff S^..E`.
   - S is root → empty tree..E so S is included.
6. Review surface = that range diff. Large files: surrounding context; findings anchored to the range.

Same standards, questions, tone, and approval bar as the rest of this skill. Read “change set” / “this diff” as the selected range.

### `scope=codebase`

Full-application health audit.

1. Map major surfaces (backend/frontend, supervisors, bootstrap, adapters).
2. Prioritize largest/central modules, recent architecture moves, cross-cutting boundaries.
3. Measure file size, ownership boundaries, repeated orchestration patterns repo-wide.
4. Structural problems that compound over time — not a single diff.

Focus:

- God files (or path to them); refactors that moved complexity instead of deleting it?
- Highest-leverage decomposition / code-judo opportunities; boundary leaks into shared paths?

## Surfaces

After the review surface exists, classify every path. Do not guess; do not skip a non-empty surface.

Path test:

- Under `docs/plans/` → plan surface. Group by top-level `docs/plans/<dir>/`. One plan job per such directory.
- Any other review-surface path → code surface. One code job if this set is non-empty.

Scope modifiers:

- `changes` / `picker`: plan dirs are those actually in the review surface (`*-pending` or `*-done`).
- `codebase`: code surface is the application tree with `docs/plans/` omitted. Plan surface is each `docs/plans/*-pending` directory. Ignore `*-done`. In-session: one plan section per pending dir, sequential. Do not ask about subagent parallelism.

Both surfaces non-empty → run both as separate labeled sections. Never drop one.

Apply [code-bar.md](code-bar.md) to each code job. Apply [plan-bar.md](plan-bar.md) to each plan job.

## Core Prompt

> Deep code quality audit of the selected review scope.
> Restructure to improve quality without changing behavior: better abstractions/modularity, less spaghetti, more succinct and legible.
> Be ambitious when a clear restructuring path exists. Thorough and rigorous. Measure twice, cut once.

Interpret scope as: `changes` → workspace git changes; `picker` → selected inclusive commit range; `codebase` → entire application.

## Review Tone

Direct, serious, demanding. Not rude — but do not soften major maintainability issues. If the code got messier or missed a dramatic simplification, say so clearly.

Good phrases:

- `this pushes the file past 1k lines. can we decompose this first?`
- `this adds another special-case branch into an already busy flow. can we move this behind its own abstraction?`
- `this works, but it makes the surrounding code more spaghetti. let's keep the behavior and restructure the implementation.`
- `i think there's a code-judo move here that makes this much simpler. can we reframe this so these branches disappear?`
- `this abstraction seems unnecessary. can we just keep the direct flow?`
- `this feels like feature logic leaking into a shared path. can we isolate it?`
- `why does this need a cast / optional here? can we make the boundary more explicit instead?`
- `this looks like a bespoke helper for something we already have elsewhere. can we reuse the canonical one?`
- `this refactor moves complexity around, but doesn't really delete it. is there a way to make the model itself simpler?`

## Output Expectations

State resolved scope: `scope=changes` | `scope=picker` | `scope=codebase`. List surfaces: `code` and/or each `docs/plans/<dir>/`. Then one complete review per job. Do not drop a job.

- **`changes`:** files from `git status`; each inspected via diff, full read, or both. Feedback actionable on workspace edits.
- **`picker`:** S and E (short hash + subject); effective git range (note root-start if used); dirty-worktree warning if any; files from the range diff and how each was inspected. Feedback actionable on the range.
- **`codebase`:** follow-up decomposition beyond any single diff is fine.

Each job follows its bar’s questions and approval bar.
