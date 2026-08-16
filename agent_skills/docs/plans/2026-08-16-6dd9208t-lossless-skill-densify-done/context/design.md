> **Archive.** Decisions in this file were current as of 2026-08-16 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# Lossless densify of plan-skill prompts

## Goal

Cut tokens from `create-multi-stage-plan/SKILL.md` and `implement-pending-plans/SKILL.md` without changing what an agent does when it follows either skill.

## Settled decisions

- Lossless means the same observable behavior: mint, picker, archive, headings, status literals, and stop rules still fire the same way. Tautologies, restated reminders, and extra examples may go. Do not repeat a fact that already has a home.
- In-place densify only. Each `SKILL.md` stays self-contained. No `references/` split, no shared companion file.
- Files in scope: the two `SKILL.md` files. The plan-id README is already at the floor — no edits, no stage.
- No Python. Do not change anything under `create-multi-stage-plan/scripts/plan-id/`.
- Frontmatter: shorten implement’s `description` only. Leave create’s `description` and both `disable-model-invocation` flags alone.
- implement structure: lead is input kinds plus discover; then one selectable-plan sentence and one stage-file sentence; `## Plan directory` owns leave / rename / disclaimer; `## Status` owns only the four literals and needs-work / skip / unusable; then Discover, Walk, Per stage, Summarize.
- The matcher paragraph is the named-plan bullet. No extracted wrapper, no “above or as,” no “wording may tighten.”
- List columns have one home: a standalone sentence before Discover (basename, path, pending/in_progress counts). Zero-match says “list selectable plans.” Several-plans says “ask with a list.” Neither arm repeats the columns or points at the other.
- create: one example path, no tautological heading glosses, mint / heading / stop contracts stay. Stages own the rewrite. Design does not list those edits.
- Two stages, one file each. No token-count gate. Stages own the rewrite; this file does not.
- Do not add any mention of an older directory grammar.

## Design

Each skill is loaded alone, so sharing a third file would not shrink a run. The waste is restatement inside a single file.

One home per fact. A pointer from one arm into another is not a home. A heading is a home only for the concept it names: archive is not Status; Status is not selectable.

create load-bearing constraints (must still be true after the rewrite): grill before write; mint CLI after resolving the skill directory; no invented id; no `--date` on the normal path; heading templates in today’s order; `None` if none; decisions not a transcript; stage map not a file listing; not implementing while planning; per-stage rationale; no TBD; no copy of `design.md` into stages; ADR stage if a decision must live; attachments linked from `design.md`.

README under `scripts/plan-id/` is already one sentence plus the invoke command. Leave it.

## Stage map

The two `SKILL.md` edits do not depend on each other. implement is first: more restatement, larger token win. create is second. README is not a stage.

## Out of scope

- Any file under `create-multi-stage-plan/scripts/plan-id/` (including README, Python, tests, lockfile)
- New files, `references/`, or a shared companion
- Token or word-count targets
- Other skills
- Changing mint CLI behavior, picker semantics, heading templates, or the archive disclaimer wording
- Mentioning or documenting any older plan-directory grammar

## Assumptions

- Each skill is injected alone when invoked, so cross-file dedup is not a prompt win.
- YAML frontmatter is part of the loaded prompt.
- `disable-model-invocation: true` stays on both skills.
- The implement `description` still needs the input kinds for the skill list; the body owns the matcher.
- Models do not need a fact restated once it has a home.
