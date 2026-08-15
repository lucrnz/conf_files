# Stage 03: Install the skill symlink

## Status
done

## Description

Symlink `jp-romaji` into `~/.agents/skills/` using the one-off pattern in `README.md`.

## Rationale

Agents load skills from `~/.agents/skills/<name>`. Without the link, `/jp-romaji` and auto-invoke will not see the skill.

## Invariants

- Per-skill symlink, not the whole repo.
- Do not move the skill out of this repo.
- Do not change other skills’ links.

## Risks

- If `~/.agents/skills/jp-romaji` exists, is not a symlink, and is not this skill: `blocked`.

## Implementation

### Files

- `~/.agents/skills/jp-romaji` (symlink)
- `~/.agents/skills/` (create if missing)

### Steps

1. `mkdir -p ~/.agents/skills`
2. If a non-symlink, unrelated `~/.agents/skills/jp-romaji` exists: `blocked`.
3. `ln -sfn "$PWD/jp-romaji" "$HOME/.agents/skills/jp-romaji"` from the agent_skills repo root.
4. Do not run the bulk install loop unless the user asked.

### Verify

```
ls -la ~/.agents/skills/jp-romaji
test -f ~/.agents/skills/jp-romaji/SKILL.md
test -f ~/.agents/skills/jp-romaji/scripts/romaji/src/romaji/cli.py
test -f ~/.agents/skills/jp-romaji/prompts/media.md
readlink -f ~/.agents/skills/jp-romaji
```

`readlink -f` must be this repo’s `jp-romaji` directory.

## Acceptance

- Symlink points at `<repo>/jp-romaji`.
- That tree includes stage 01 CLI and stage 02 skill files.
- Other `~/.agents/skills/` entries unchanged.
- Do not rename this plan directory here (`implement-pending-plans` does that when every stage is `done`).
