# Stage 03: create-multi-stage-plan write grammar

## Status
done

## Description

Rewrite the naming section of `create-multi-stage-plan/SKILL.md` so new plan directories come from the stage 01 CLI. This is the write switch. Stage files stay `{stageNN}-{stage-slug}.md`.

## Rationale

The create skill is the only writer. implement-pending-plans already lists `-pending` and (after stage 02) matches basenames and hyphen-fields. Turning on mint here cannot hide new directories.

## Invariants

- New plan path template is `docs/plans/{YYYY-MM-DD}-{id}-{slug}-pending/`.
- The agent never invents `{id}` and never derives it by scanning sibling prefixes.
- Skill-dir resolution matches `jp-romaji`: this skill lives in the directory that contains this `SKILL.md`; follow the symlink; never invoke with a cwd-relative `create-multi-stage-plan/scripts/plan-id` from the target repo.
- `uv` is required. Mint failure ⇒ stop; do not write a plan directory.
- `{stageNN}-{stage-slug}.md` is unchanged.
- This file is the living write contract. It does not restate alphabet, length, or retry internals the CLI owns.

## Risks

- An agent that mkdirs a name it invented defeats the stage. The mint invocation is a required step, not an example.
- Extra sentences about other name shapes do not belong here. Replace the write-path diagram and naming bullets with the mint flow only.

## Implementation

### Files

- `create-multi-stage-plan/SKILL.md`

### Steps

1. Replace the write-path diagram and examples with:

   `docs/plans/2026-08-16-v1stgxr8-checkout-rewrite-pending/`

   Keep `context/design.md` and `{stageNN}-{stage-slug}.md` as they are.
2. Replace the shared-counter naming bullet with:
   1. Ensure `docs/plans/` exists in the target repo.
   2. Resolve this skill’s directory. Run:

      `uv run --project <that-dir>/scripts/plan-id plan-id mint --plans-dir docs/plans --slug {plan-slug}`

   3. Use the single stdout line as the directory basename. Create that directory. Then write `context/` and stages as today.
   4. If mint exits non-zero, stop and report stderr. Do not pick an id by hand.
3. Date in the name comes from the CLI. Do not ask the user for a date. Do not pass `--date` on the normal path.
4. `{plan-slug}` / `{stage-slug}` stay short kebab-case. Note that the CLI rejects any other slug.
5. Keep “New plan directories always end in `-pending`” and the stage-file rule.
6. Do not mention implement-pending-plans selectors.

### Verify

- `create-multi-stage-plan/SKILL.md` contains the `uv run --project <that-dir>/scripts/plan-id plan-id mint` invoke line and an explicit mint-failure ⇒ stop / do-not-invent-an-id requirement.
- The write-path example is `docs/plans/2026-08-16-v1stgxr8-checkout-rewrite-pending/` (or the same shape).
- Stage-file template is still `{stageNN}-{stage-slug}.md`.
- `implement-pending-plans/SKILL.md` is not edited in this stage.

## Acceptance

- Following the create skill produces `{date}-{id}-{slug}-pending` directories from mint stdout.
- Following the create skill cannot skip the mint CLI or invent `{id}`.
- Stage numbering and `context/` layout are unchanged.
- The skill does not re-specify id alphabet, length, or retry count.
