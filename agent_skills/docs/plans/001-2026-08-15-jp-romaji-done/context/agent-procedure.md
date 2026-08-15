# Agent procedure

Plan-time attachment. Living copy after stage 02: `jp-romaji/SKILL.md` (procedure only). Do not paste house style, the authority list, or blast radius into `SKILL.md`.

## Classify (required first)

Default: `generic`.

Flip to media when the user/caller **says** it is media (lyrics, anime line, VN, song, …) **or** **names a work** (“Idol by YOASOBI”, “Evangelion title”). Do not infer media from “this text looks like lyrics.”

If media and the subtype is not given: infer `lyrics` | `title/name` | `dialogue` | `mixed`, **state** it, allow override.

`mixed`: per-line subtype.

If `generic` and there is no Japanese and no named work: ask for text. Stop.

## Pipeline

Resolve the directory that contains this `SKILL.md` (follow the symlink). Then:

```
uv run --project <that-dir>/scripts/romaji romaji --engine both
```

Never a cwd-relative `jp-romaji/scripts/romaji` (that only works as cwd in this repo). Do not write `$SKILL_DIR`.

1. Classify and state the mode.
2. **Has source lines** (user pasted Japanese):
   1. Run the CLI on those lines.
   2. Spawn **one** child (`reader`).
      - `generic`: attach `house-style.md` + `prompts/generic.md`. No web tools.
      - media: attach `house-style.md` + `prompts/media.md`. Child may use the web. Do not research in the main agent.
   3. Fuse the three voters. Emit.
3. **No source lines, media** (named work):
   1. Spawn the media child with the work identifier, mode, and house-style + media prompt. No engine JSON.
   2. Child returns `fetched_lines` + per-line votes + `sources`.
   3. Main agent runs the CLI on `fetched_lines`.
   4. Fuse the three voters. Emit.
4. Main agent never browses on a media run. Generic child never browses.

## Fusion

Vote on `hira` / intended reading. Then apply `house-style.md` to the winning reading.

Carve-out: well-attested official Latin names/works/characters stay official.

Voters: `pykakasi` | `cutlet` | `reader`. The reader is the generic child or the media child. A voter that did not run does not vote and does not block +15. There is no separate research ballot; media `sources` and `variant` are appendix fields.

Tie-break when two candidates are within 10 confidence points:

1. Reading shared by more voters
2. reader
3. cutlet
4. pykakasi

Then house-normalize (except official Latin names/works). Same reading with different spellings (`Toukyou` / `Tōkyō` / `Tokyo`) is not a conflict.

## Confidence

Integer 0–100, per line and overall. Number + one-line reason.

Path ∈ {`pykakasi`, `cutlet`, `reader`}. Prior from the **winning path**:

- Mechanical winner (`pykakasi` or `cutlet`) on kanji-heavy text: cap 55
- Mechanical winner on non-kanji text: 70
- Reader winner on media: cited-tier prior in `prompts/media.md` only (do not restate the numbers here)
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

Same list as [design.md](./design.md) § Out of scope. `SKILL.md` may link that list in one short bullet block, not a second policy essay.
