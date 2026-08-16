# Code bar

Each theme: **rule** / **flag** / **remedy**. Apply all. Push hard — these are non-negotiable review pressures, not optional style notes.

## Review Themes

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
