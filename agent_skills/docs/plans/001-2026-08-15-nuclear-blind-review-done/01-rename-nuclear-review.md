# Stage 01: Rename thermo-nuclear to nuclear-review

## Status
done

## Description

Rename the existing skill directory and frontmatter from `thermo-nuclear-code-quality-review` to `nuclear-review`. Update description/trigger wording so the slash command is `/nuclear-review`. Leave review behavior unchanged.

## Rationale

Later stages add files beside this skill and teach the blind skill to point at it. Doing the rename first means no stage has to mention the old path except as something already gone.

## Invariants

- The skill is still slash-only (`disable-model-invocation: true`).
- Scope table, workflows, themes, tone, output, and approval bar are unchanged in this stage.
- No trampoline directory or old-name skill remains in the repo.

## Risks

- Existing `~/.agents/skills/thermo-nuclear-code-quality-review` symlinks become stale until the README install loop is re-run and the old link is removed. This stage must say that in the skill? No — the implementer does it as a verify/install step, not as skill prose.

## Implementation

### Files

- `thermo-nuclear-code-quality-review/SKILL.md` → `nuclear-review/SKILL.md` (move)
- Any in-repo string that names `thermo-nuclear-code-quality-review` (grep; expect only this skill)

### Steps

1. Move the directory `thermo-nuclear-code-quality-review/` to `nuclear-review/`.
2. Set frontmatter `name: nuclear-review`. Rewrite `description` triggers to nuclear review / `/nuclear-review` while keeping the same meaning (strict maintainability review; same scopes).
3. Rename the H1 to match (e.g. `Nuclear Review`). Do not edit themes, workflows, or the approval bar.
4. Grep the repo for `thermo-nuclear` and `thermonuclear`; leave none that refer to this skill.
5. Re-run the README symlink loop. Remove `~/.agents/skills/thermo-nuclear-code-quality-review` if it still exists.

### Verify

- `test -f nuclear-review/SKILL.md` and `test ! -e thermo-nuclear-code-quality-review`
- Frontmatter `name:` is `nuclear-review`
- `rg -n 'thermo-nuclear|thermonuclear' --glob '!docs/plans/001-2026-08-15-nuclear-blind-review-pending/**'` returns no skill references
- `ls -la ~/.agents/skills/nuclear-review` is a symlink to this repo’s `nuclear-review/`

## Acceptance

- The only review skill directory in this repo is `nuclear-review/`.
- `/nuclear-review` is the skill name. The old slash name is gone in-repo.
- Review body (scopes, themes, approval) is the pre-rename text aside from the title/name/triggers.
