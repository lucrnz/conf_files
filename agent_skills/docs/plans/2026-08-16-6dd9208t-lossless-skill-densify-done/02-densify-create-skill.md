# Stage 02: Densify create-multi-stage-plan

## Status

done

## Description

Rewrite `create-multi-stage-plan/SKILL.md` in place: one example path, no tautological glosses, no restated tree facts. Mint protocol, heading templates, and stop rules stay.

## Rationale

Smaller file than implement, but the tree/examples/glosses are the other half of the prompt bloat. Independent of stage 01.

## Invariants

- Still grill (or question tool with recommended option first) before writing; never write while multi-option.
- Still mint via `uv run --project <that-dir>/scripts/plan-id plan-id mint --plans-dir docs/plans --slug {plan-slug}` after resolving this skill’s directory (follow the install symlink). `uv` required. Never a cwd-relative `create-multi-stage-plan/scripts/plan-id` from the target repo.
- Non-zero mint: stop, report stderr. Do not pick an id by hand, invent `{id}`, or scan sibling prefixes. Do not ask the user for a date. Do not pass `--date` on the normal path.
- Directory tree, `context/design.md` heading template, and stage heading template (including `Status` / `pending`) stay, same order.
- One concrete example path remains.
- Stages only at the plan root; everything else under `context/`.
- Do not implement the plan this skill writes. Summarize and stop.
- No Python. No README edit. No other files.

## Risks

Dropping a load-bearing gloss (not a transcript, not a file listing, `None` if none, not implementing, per-stage rationale, no TBD, no copy into stages, ADR-if-must-live, attachments must be linked) looks like densify and changes output quality.

## Implementation

### Files

- `create-multi-stage-plan/SKILL.md`

### Steps

1. Leave YAML `name`, `description`, and `disable-model-invocation` unchanged.

2. Keep sections 1 (Resolve decisions), 2 (Decompose), and 4 (Stop) as they are, aside from deleting a sentence only if it is a word-for-word repeat of another surviving sentence. Do not drop grilling, recommended-option-first, dependency-then-impact, or “do not implement / summarize / stop”.

3. Section 3 opening: one sentence that creates `docs/plans/` if missing and always starts a **new** plan directory (do not append). Then the existing tree fence:

   ```
   docs/plans/{YYYY-MM-DD}-{id}-{plan-slug}-pending/
     context/design.md
     context/{attachment}
     {stageNN}-{stage-slug}.md
   ```

4. One write-order sentence: write `context/` first (`design.md`, then attachments), then stage files. Do not say this again under Naming.

5. Examples: keep exactly this line (or the same path in a one-line fence):

   `docs/plans/2026-08-16-v1stgxr8-checkout-rewrite-pending/context/design.md`

   Delete the two `01-extract-pricing.md` / `02-swap-payment-adapter.md` example lines.

6. Naming, in this order, without a “ensure `docs/plans/` exists” step:
   - Resolve this skill’s directory (the directory that contains this `SKILL.md`; follow the symlink if reached via `~/.agents/skills/create-multi-stage-plan`). Then:

     `uv run --project <that-dir>/scripts/plan-id plan-id mint --plans-dir docs/plans --slug {plan-slug}`

     Never invoke with a cwd-relative `create-multi-stage-plan/scripts/plan-id` path from the target repo. `uv` is required.
   - Use the single stdout line as the directory basename. Create that directory.
   - If mint exits non-zero, stop and report stderr. Do not pick an id by hand. Do not invent `{id}` and do not derive it by scanning sibling prefixes.
   - `{YYYY-MM-DD}` and `{id}` come from the mint CLI. Do not ask the user for a date. Do not pass `--date` on the normal path.
   - `{plan-slug}` / `{stage-slug}`: short kebab-case. The CLI rejects any other slug.
   - `{stageNN}`: 2-digit, zero-padded (`01`, `02`, …). Stages of one plan start at `01` and increase in execution order.
   - Stages are `{stageNN}-{stage-slug}.md` at the plan root only. Everything else goes under `context/`.

   Do not add a “always end in `-pending`” bullet.

7. Keep both heading templates as fenced markdown, same heading order as today.

8. After the `design.md` template, keep only:
   - Settled decisions: grilling outcomes as decisions, not a transcript
   - Stage map: dependencies and why this order — not a file listing
   - Out of scope / Assumptions: `None` if there are none
   - Do not copy `design.md` sections into stages; stages may link to `design.md` or a `context/` attachment; do not put Implementation steps, file lists, or Acceptance in `design.md`
   - If a decision must live past this plan, add a stage that writes it to the project’s normal docs/ADRs. Do not treat `design.md` as living documentation
   - Attachments under `context/` only when they would bloat `design.md`; every attachment must be linked from `design.md`

   Delete the Goal and Design one-liners.

9. After the stage template, keep only:
   - Status: `pending` — you are not implementing, just planning
   - Rationale: why this stage exists / its payoff (per-stage, not the whole-plan story)
   - Invariants / Risks: `None` if none
   - Files: paths this stage will create or change; `None` if no path changes
   - Vague “it works” or TBD is not done planning — rewrite

   Delete the Description, Steps, Verify, and Acceptance one-liners.

10. Do not edit `scripts/plan-id/` (README, Python, tests, lockfile). Do not add a mention of any older directory grammar.

### Verify

- `rg -n 'plan-id mint --plans-dir docs/plans --slug' create-multi-stage-plan/SKILL.md` — mint command present.
- `rg -n 'cwd-relative|Do not invent|scanning sibling|--date' create-multi-stage-plan/SKILL.md` — all four mint constraints present.
- `rg -n 'v1stgxr8-checkout-rewrite-pending' create-multi-stage-plan/SKILL.md` — exactly one example basename.
- `rg -n '01-extract-pricing|02-swap-payment-adapter' create-multi-stage-plan/SKILL.md` — no hits.
- `rg -n 'not a transcript|not a file listing|not implementing|per-stage' create-multi-stage-plan/SKILL.md` — load-bearing glosses present.
- `rg -n 'None if' create-multi-stage-plan/SKILL.md` — empty Out of scope / Assumptions / Invariants / Risks / Files still allowed.
- `rg -n 'TBD' create-multi-stage-plan/SKILL.md` — vague/TBD rewrite still required.
- `rg -n 'living documentation|must be linked' create-multi-stage-plan/SKILL.md` — ADR/archive and attachment-link rules present.
- Heading fences still contain `# {plan title}`, `## Settled decisions`, `## Stage map`, `# Stage {stageNN}`, `### Files`, `### Verify`, `## Acceptance`.
- `git diff --stat -- create-multi-stage-plan/scripts/plan-id` is empty.
- `wc -w create-multi-stage-plan/SKILL.md` — report before/after; not a gate.

## Acceptance

- YAML frontmatter unchanged.
- Exactly one example path, the `…/context/design.md` line in step 5.
- Mint resolve + command + failure/no-invent/`--date`/kebab/`stageNN` rules all present.
- Both heading templates present in the same order as today.
- Goal/Design/Description/Steps/Verify/Acceptance tautological one-liners are gone. Every load-bearing gloss in steps 8–9 remains.
- An agent following only this file still writes the same directory shape and the same section contracts, and still stops without implementing.
- No file outside `create-multi-stage-plan/SKILL.md` changed.
