---
name: jp-romaji
description: Convert Japanese text to speakable ASCII Hepburn romaji. Assumes a generic run (pykakasi + cutlet + one no-web LLM) unless the user/caller marks it as media or names a work; media runs add a researching LLM subagent. Fuses on reading with a 0–100 confidence score and prints winning romaji plus a comparison appendix. Use when the user wants romaji, romanize Japanese, lyrics in romaji, JP→romaji, Hepburn, song/anime/VN romanization, or runs /jp-romaji.
---

# jp-romaji

Convert Japanese to speakable ASCII Hepburn romaji. House style: [house-style.md](house-style.md). Reader prompts: [prompts/generic.md](prompts/generic.md), [prompts/media.md](prompts/media.md).

## Classify (required first)

Default: `generic`.

Flip to media when the user/caller **says** it is media (lyrics, anime line, VN, song, …) **or** **names a work** (“Idol by YOASOBI”, “Evangelion title”). Do not infer media from “this text looks like lyrics.”

If media and the subtype is not given: infer `lyrics` | `title/name` | `dialogue` | `mixed`, **state** it, allow override. `mixed` is per-line.

If `generic` and there is no Japanese and no named work: ask for text. Stop.

## Mechanical CLI

This skill lives in the directory that contains this `SKILL.md`. Follow the symlink if you reached it via `~/.agents/skills/jp-romaji`. Resolve that directory, then:

```
uv run --project <that-dir>/scripts/romaji romaji --engine both
```

Feed source lines on stdin (or a temp file). Parse JSONL. Each line is `orig` plus `pykakasi` and `cutlet` objects (`hira`, `kana`, `romaji`, `tokens`).

Never invoke the CLI with a cwd-relative `jp-romaji/scripts/romaji` path.

## Pipeline

1. Classify and state the mode.
2. **Has source lines** (user pasted Japanese):
   1. Run the CLI on those lines.
   2. Spawn **one** child (`reader`). Attach [house-style.md](house-style.md) plus the matching prompt. Give it mode, lines, and both engine JSON objects.
      - `generic`: [prompts/generic.md](prompts/generic.md). **No web/search tools.**
      - media: [prompts/media.md](prompts/media.md). Child may use the web. **Do not research in the main agent.**
   3. Fuse the three voters. Emit.
3. **No source lines, media** (named work):
   1. Spawn the media child with the work identifier, mode, [house-style.md](house-style.md), and [prompts/media.md](prompts/media.md). No engine JSON.
   2. Child returns `fetched_lines` + per-line votes + `sources`.
   3. Run the CLI on `fetched_lines`.
   4. Fuse the three voters. Emit.
4. Main agent never browses on a media run. Generic child never browses.

If a child does not return parseable JSON, ask it once to resend the object only, then proceed or report the failure. Do not invent readings to fill a broken blob.

## Fusion

Vote on `hira` / intended reading. Then apply [house-style.md](house-style.md) to the winning reading.

Carve-out: well-attested official Latin names/works/characters stay official.

Voters: `pykakasi` | `cutlet` | `reader`. The reader is the generic child or the media child. A voter that did not run does not vote and does not block +15. There is no separate research ballot; media `sources` and `variant` are appendix fields.

Treat two `hira` strings as the same reading if they match after removing spaces and converting katakana long-vowel `ー` to the previous vowel’s hiragana length. `Toukyou` / `Tōkyō` / `Tokyo` as romaji are not a conflict when `hira` matches.

Tie-break when two candidates are within 10 confidence points:

1. Reading shared by more voters
2. reader
3. cutlet
4. pykakasi

Then house-normalize (except official Latin names/works).

## Confidence

Integer 0–100, per line and overall. Number + one-line reason.

Path ∈ {`pykakasi`, `cutlet`, `reader`}. Prior from the **winning path**:

- Mechanical winner (`pykakasi` or `cutlet`) on kanji-heavy text: cap 55
- Mechanical winner on non-kanji text: 70
- Reader winner on media: use the cited-tier prior in [prompts/media.md](prompts/media.md). Do not copy those numbers here.
- Reader winner on generic: 40–65 (no source tier)

Then one agreement bonus, not stacked, over voters that **ran**:

- +10 if exactly 2 of 3 share the winning reading
- +15 if every voter that ran shares the winning reading
- −15 if the pick is reader-only (neither engine shares that reading)

If any line is below 60, overall cannot be above 75. Report the min line score in the appendix.

## User-visible output

1. Stated mode (and inferred subtype if any).
2. Copy-paste block: winning house-style romaji, one line per source line.
3. Appendix:
   - columns (both modes): pykakasi | cutlet | reader | **pick**
   - all columns romaji
   - per-line confidence + reason; overall; min line
   - media only: `sources` and `variant` / official line from the child (not extra vote columns)

Internal kana only appears if it is the reason.

## Out of scope

- Translation / gloss, audio/PV transcription, Chinese/Korean romanization
- User-facing kana/furigana, silent rewrite of the user’s Japanese, Anki export
- Dumping a whole series/game/VN
- Inferring media from “this looks like lyrics” without a mention or a named work
- Main-agent web research on a media run
