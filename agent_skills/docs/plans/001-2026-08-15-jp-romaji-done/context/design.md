**Archive.** Decisions in this file were current as of 2026-08-15 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# jp-romaji

## Goal

Create the `jp-romaji` skill: Japanese → speakable ASCII Hepburn romaji, with a winning romaji block plus a comparison appendix and a 0–100 confidence score.

Default run is **generic** (engines + no-web LLM). **Media** only when the caller marks it or names a work.

## Settled decisions

- Name `jp-romaji` at repo `jp-romaji/`. Auto-invoke and `/jp-romaji`. No `disable-model-invocation`.
- Description (verbatim):

  > Convert Japanese text to speakable ASCII Hepburn romaji. Assumes a generic run (pykakasi + cutlet + one no-web LLM) unless the user/caller marks it as media or names a work; media runs add a researching LLM subagent. Fuses on reading with a 0–100 confidence score and prints winning romaji plus a comparison appendix. Use when the user wants romaji, romanize Japanese, lyrics in romaji, JP→romaji, Hepburn, song/anime/VN romanization, or runs /jp-romaji.

- Speak/sing job. Full media types exist but are opt-in. Input is paste and/or a named work.
- Classify first. Default `generic`. Flip to media if the user/caller says it is media **or** names a work. If media and subtype is missing: infer `lyrics` | `title/name` | `dialogue` | `mixed`, state it, allow override. `mixed` is per-line.
- Generic: both engines + one no-web LLM. No research. Spoken house style.
- Media: one child given `prompts/media.md`. That child owns fetch + reading research. Main agent does not browse.
- Named work, no paste: media child fetches and votes (no engine JSON). Main agent then runs the CLI on `fetched_lines` and fuses. Paste is always the source; never expand a partial paste; never silent-replace.
- Fuse on **reading**, then house-style. Official Latin names/works carved out. Three voters: `pykakasi` | `cutlet` | `reader` (generic or media child). Media adds sources and variant flags, not a fourth vote. Scoring: [agent-procedure.md](./agent-procedure.md). Reader evidence priors: [prompt-media.md](./prompt-media.md).
- Mechanical CLI: one uv project, argparse, `--engine` default `both`, JSONL, no house style. [json-contract.md](./json-contract.md). Tests synthetic only.
- Living files: `SKILL.md` (procedure + CLI invoke), `house-style.md`, `prompts/generic.md`, `prompts/media.md` (authority list + blast radius live **only** here). [house-style.md](./house-style.md), [prompt-generic.md](./prompt-generic.md), [prompt-media.md](./prompt-media.md).
- SKILL.md tells the agent to resolve the directory that contains `SKILL.md` (follow the symlink) and run `uv run --project <that-dir>/scripts/romaji romaji --engine both`. No `$SKILL_DIR`. Never cwd-relative `jp-romaji/scripts/romaji`.
- Three stages. Rewrite of this plan in place. First Python/uv/pytest skill in this repo.

## Design

An agent procedure plus a dumb dual-engine CLI.

Main agent: classify → run CLI when source lines exist → spawn exactly one child with the matching prompt file and `house-style.md` → if the child returned `fetched_lines`, run the CLI on those, then fuse → emit romaji + appendix.

Children: generic never uses the web. Media child searches, fetches, and votes. Fusion and house style stay in the main agent.

Normative attachments (do not restate them in stages): [json-contract.md](./json-contract.md), [house-style.md](./house-style.md), [agent-procedure.md](./agent-procedure.md), [prompt-generic.md](./prompt-generic.md), [prompt-media.md](./prompt-media.md).

## Stage map

Build the converter (package, CLI, tests) first so the skill can name a real command and JSON shape. Write every living skill file in one stage after that, so there is no stub `SKILL.md` and no second copy of house style or prompts. Install last.

## Out of scope

- Translation / gloss, audio/PV transcription, Chinese/Korean romanization
- User-facing kana/furigana, silent rewrite of the user’s Japanese, Anki export
- Dumping a whole series/game/VN
- House style inside `scripts/romaji`
- Copyrighted lyrics as fixtures
- A second LLM child on one run
- Full UniDic; catalog VocaDB as the global style
- Main-agent web research on a media run
- Inferring media from “this looks like lyrics” without a mention or a named work

## Assumptions

- `uv` works here; `fugashi` wheels install; Python `>=3.11`.
- `agents/openai.yaml` exists; implicit invocation stays on.
- After install, agents resolve the skill directory as the directory that contains `SKILL.md` (the `~/.agents/skills/jp-romaji` symlink).
- `context/` is plan-time. Living copies are under `jp-romaji/` after stage 02.
