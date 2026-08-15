# Stage 02: Skill procedure, house style, and prompts

## Status
done

## Description

Write every living skill file once: `SKILL.md`, `agents/openai.yaml`, `house-style.md`, `prompts/generic.md`, `prompts/media.md`. No stub. Copy rules from the attachments; do not invent a second copy.

## Rationale

The CLI is real. One write avoids a disposable `SKILL.md` and keeps one home per fact.

## Invariants

- Frontmatter `name` / `description` are the verbatim text in [design.md](./context/design.md).
- No `disable-model-invocation`.
- CLI invoke in `SKILL.md`: resolve the directory that contains `SKILL.md`, then `uv run --project <that-dir>/scripts/romaji`. No `$SKILL_DIR`. No cwd-relative `jp-romaji/scripts/romaji`.
- Fusion is three voters (`pykakasi`, `cutlet`, `reader`). No research vote column.
- House style lives only in `jp-romaji/house-style.md`.
- Authority list, blast radius, and reader evidence priors live only in `jp-romaji/prompts/media.md`.
- No `jp-romaji/references/`.

## Risks

- Pasting house style or the authority list into `SKILL.md` creates drift. Do not.

## Implementation

### Files

- `jp-romaji/SKILL.md` (create)
- `jp-romaji/agents/openai.yaml` (create)
- `jp-romaji/house-style.md` (create; body from [house-style.md](./context/house-style.md) without the plan-time header)
- `jp-romaji/prompts/generic.md` (create; body from [prompt-generic.md](./context/prompt-generic.md) without the plan-time header)
- `jp-romaji/prompts/media.md` (create; body from [prompt-media.md](./context/prompt-media.md) without the plan-time header)

### Steps

1. Write `SKILL.md` from [agent-procedure.md](./context/agent-procedure.md): classify, pipeline (including fetch-then-engines), three-voter fusion, confidence (priors for media reader linked to `prompts/media.md`, not copied), appendix columns `pykakasi | cutlet | reader | pick`, skill-dir resolve + `uv` command, spawn rules (generic = no web; media = child researches). Link `house-style.md` and the two prompt files. Short out-of-scope bullets matching [design.md](./context/design.md).
2. Write `agents/openai.yaml` like `domain-modeling/agents/openai.yaml`. Display name `JP Romaji`. Do not set `allow_implicit_invocation: false`.
3. Copy house-style and prompt attachments into the living files (strip “plan-time attachment” notes).
4. Do not add Python house style. Do not add a third prompt.

### Verify

Read `jp-romaji/SKILL.md` and confirm: approved description; default `generic`; named-work flip; skill-dir resolve (no `$SKILL_DIR`); one child; three voters; no cwd-relative `jp-romaji/scripts/romaji`; no restated authority list or prior numbers; no restated particle table. Confirm the three sibling files exist and contain the attachment bodies.

## Acceptance

- An agent with only `jp-romaji/` can classify, run the real CLI, spawn the right child, fuse, score, and format the appendix.
- Description matches [design.md](./context/design.md) verbatim.
- `prompts/media.md` is the only authority, blast-radius, and reader-prior text.
- `house-style.md` is the only house-style text.
- No TBD/TODO. No keyword-assert theater required.
