---
name: thermo-nuclear-code-quality-review
description: Extremely strict maintainability review (abstraction quality, giant files, spaghetti growth). Triggers: thermo-nuclear / thermonuclear review, deep code quality audit, harsh maintainability review. Default scope=changes; also scope=codebase or scope=picker / picker for an inclusive commit range.
disable-model-invocation: true
---

# Thermo-Nuclear Code Quality Review

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

Examples: `thermo-nuclear review` → `changes`; `… scope=codebase` → `codebase`; `… picker` → `picker`.

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

## Core Prompt

> Deep code quality audit of the selected review scope.
> Restructure to improve quality without changing behavior: better abstractions/modularity, less spaghetti, more succinct and legible.
> Be ambitious when a clear restructuring path exists. Thorough and rigorous. Measure twice, cut once.

Interpret scope as: `changes` → workspace git changes; `picker` → selected inclusive commit range; `codebase` → entire application.

## Review Themes

Each theme: **rule** / **flag** / **remedy**. Apply all. Push hard — these are non-negotiable review pressures, not optional style notes.

### 0. Ambition / code judo

- **Rule:** Prefer restructurings that preserve behavior while making the implementation dramatically simpler. Delete complexity; don’t stop at local cleanup. Push the solution that feels inevitable in hindsight. Do **not** settle for “maybe rename this” or a cleaner version of the same messy idea when a simpler idea is plausible.
- **Flag:** Complicated implementation where a reframing would erase whole categories of complexity; refactors that move concepts around without reducing them.
- **Remedy:** Delete a layer of indirection; reframe the model so branches disappear; change ownership so the feature is a natural extension of an existing abstraction.

### 1. File size (~1k lines)

- **Rule:** Do not push a file from under 1k to over 1k lines without a very strong reason. Prefer extract helpers/modules first. Waive only if there is a compelling structural reason **and** the resulting file is still clearly organized.
- **Flag:** Diff crosses ~1000 lines, especially when the new code could be split out.
- **Remedy:** Split into focused modules; extract helpers/subcomponents before growing the file.

### 2. Spaghetti / special-case growth

- **Rule:** No ad-hoc conditionals, scattered special cases, or one-off branches bolted onto unrelated flows. Design problem, not a nit.
- **Flag:** Weird ifs in random places; one-off booleans/nullable modes; temporary branching likely to become permanent debt; edge cases mid busy function; copy-pasted logic instead of an extracted helper.
- **Remedy:** Dedicated abstraction, helper, state machine, policy object, or module; default flow with fewer exceptions; collapse duplicate branches.

### 3. Clean design over “it works”

- **Rule:** Same behavior, cleaner structure → push for cleaner. Prefer removing moving pieces over spreading the same complexity.
- **Flag:** Rubber-stamped working code that leaves the codebase messier; tests pass but modularity/readability worsen.
- **Remedy:** Simpler default path; separate orchestration from business logic; delete complexity rather than polish it.

### 4. Direct over magical

- **Rule:** Prefer direct, boring, maintainable code. Brittle/ad-hoc/magic behavior is a quality problem. Thin wrappers that don’t buy clarity are debt.
- **Flag:** Generic mechanisms hiding simple data shapes; identity/pass-through helpers; unnecessary indirection.
- **Remedy:** Keep the direct flow; delete wrappers that don’t clarify the API.

### 5. Types and boundaries

- **Rule:** Question needless optionality, `unknown`/`any`, cast-heavy code when a clearer boundary exists. Prefer explicit models/contracts.
- **Flag:** Casts, optionality, or ad-hoc objects that obscure the invariant; silent fallbacks papering over unclear boundaries.
- **Remedy:** Explicit typed models or shared contracts; replace condition chains with a typed model or explicit dispatcher; make the boundary explicit so control flow simplifies.

### 6. Canonical layer and helpers

- **Rule:** Logic lives in the right package/module/layer. Reuse canonical utilities over bespoke one-offs. No feature logic in shared paths; no implementation details leaking through APIs.
- **Flag:** Feature checks scattered through general-purpose code; near-duplicate or copy-pasted helpers; wrong-layer ownership; details leaking across API boundaries.
- **Remedy:** Move to the owner of the concept; reuse the canonical helper; isolate feature-specific logic behind a dedicated boundary.

### 7. Orchestration and atomicity

- **Rule:** Flag avoidable sequential orchestration and partial updates when a cleaner structure is obvious. Not micro-optimization theater.
- **Flag:** Independent work serialized for no reason; updates that leave half-applied state.
- **Remedy:** Parallelize independent work when it clarifies the flow; restructure related updates into a more atomic operation.

## Primary Review Questions

For every meaningful change or module in scope:

1. Code-judo move that would make this dramatically simpler?
2. Does this improve or worsen local architecture / couple or clutter a cohesive module?
3. Did we cross a healthy file-size boundary?
4. New branching where a better abstraction belongs?
5. Direct and legible, or special cases and incidental control flow?
6. Abstraction earning its keep, or just a wrapper?
7. Right layer? Clear types/contracts, or casts/optionality/ad-hoc shapes?
8. Orchestration more sequential or less atomic than it needs to be?

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

State resolved scope: `scope=changes` | `scope=picker` | `scope=codebase`.

- **`changes`:** files from `git status`; each inspected via diff, full read, or both. Feedback actionable on workspace edits.
- **`picker`:** S and E (short hash + subject); effective git range (note root-start if used); dirty-worktree warning if any; files from the range diff and how each was inspected. Feedback actionable on the range.
- **`codebase`:** follow-up decomposition beyond any single diff is fine.

Prioritize findings:

1. Structural regressions and missed code-judo simplifications
2. Spaghetti / branching growth and boundary–abstraction–type issues
3. File-size, decomposition, modularity
4. Legibility nits last — fewer high-conviction comments beat a flood of cosmetics

## Approval Bar

Do not approve merely because behavior seems correct. Approve only when there is no clear structural regression, no obvious missed code-judo path, no unjustified ~1k-line explosion, no spaghetti growth, no magic/wrapper/cast churn obscuring design, and no boundary leak or canonical-helper duplication.

**Do not approve** (unless clearly justified) when the change set:

- preserves incidental complexity despite a visible code-judo path
- pushes a file from under ~1k to over ~1k lines (waive only if compelling structural reason **and** the file remains clearly organized)
- adds ad-hoc branching that tangles an existing flow
- scatters feature checks through shared code, leaks implementation details through APIs, or puts logic in the wrong layer
- adds unnecessary abstraction/wrapper or cast-heavy contracts that obscure the design
- duplicates a canonical helper or copy-pastes logic that should be extracted

If any apply, leave explicit actionable feedback and push for cleaner decomposition.
