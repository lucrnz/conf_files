# House romanization style

Audience: speak or sing the line. Do not implement these rules in `scripts/romaji`. Prompts attach this file; they do not copy it.

## System

Modified Hepburn, ASCII-only.

## Mode families

- `generic` and `dialogue`: spoken.
- `lyrics`: sung.
- `title/name`: official Latin for the whole title if it exists; else title-case house style; spoken particles.
- `mixed`: apply this file per line’s subtype.

## Particles

- Topic `は` → `wa`
- Direction `へ` → `e`
- Object `を`:
  - sung (`lyrics`) → `wo`
  - spoken (`generic`, `dialogue`, `title/name`) → `o`
- Non-particle `は`/`へ`/`を` follow the word’s actual reading (`ha` / `he` / `wo`).

## Vowels and ん

- Long vowels: `ou` / `uu` / `ii` / `ee` / `aa`. No macrons or circumflexes.
- Katakana `ー`: same long-vowel spelling as the preceding vowel.
- `ん` → `n`, but `n'` before a vowel or `y`.
- `ん` before `b`/`p`/`m`: `n` (not `m`).
- `づ` → `zu`.
- Small `っ` → doubled following consonant.

## Spacing and case

- Spaces between words and particles.
- Prefer cutlet tokenization as the spacing prior; particles stay separate in the emit.
- `generic`, `dialogue`, `lyrics`: sentence case.
- `title/name` with no official Latin: Title Case; do not capitalize single-kana particles (`wa`, `ga`, `o`, `e`, `ni`, `no`, `to`, `de`, `mo`, `ya`, `ka`).
- Honorifics: dash (`onee-san`).
- Personal names keep original order (usually family name then given name).

## Names, loanwords, English

- Well-attested official Latin for artists, works, and characters stays even inside a line. Do not invent stylization.
- Lyric/dialogue/generic wording: intended reading, then this style.
- A published official romaji lyric sheet is a reading hint, not a verbatim override (except official names/titles).
- Katakana loanwords are phonetic (`コーヒー` → `koohii`), not `coffee`.
- Actual English or official Latin already in the source line stays. Do not Hepburn-ize `I love you` unless the source is kana.

## Examples (agent-side, not CLI tests)

| Mode | Japanese | House romaji |
|---|---|---|
| generic / dialogue | 地球最後の告白を | `chikyuu saigo no kokuhaku o` |
| lyrics | 地球最後の告白を | `chikyuu saigo no kokuhaku wo` |
| generic | 恋は戦争 | `koi wa sensou` |
| title (no official) | 歌に形はないけれど | `Uta ni Katachi wa Nai Keredo` |
| any | コーヒー | `koohii` |
| any | してやんよ | `shiteyan'yo` |
