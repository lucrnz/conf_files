# Stage 03: Skill DEPENDENCIES.md and auto-install

## Status
done

## Description

Add a parseable `ask-user/DEPENDENCIES.md` that lists `shorten-url`, and teach AGENTS.md plus the Agents README one-off to install those siblings when installing a skill.

## Rationale

Stage 02’s path-dep makes a one-skill dest copy of ask-user unrunnable unless shorten-url is copied too. The dep list belongs in the skill; the procedure belongs in the install docs.

## Invariants

- AGENTS.md does not name `shorten-url`. That name lives in `ask-user/DEPENDENCIES.md`.
- A listed name that is not a repo skill (no `SKILL.md` under `REPO/<name>/`) is an error. Do not invent or skip it.
- Recurse through dependency files. Skip a name already visited in this install.
- Dest-only OpenCode skills stay dest-only. “update my opencode skills” still leaves them alone.
- No new install program. Agents follow the documented shell procedure.

## Risks

An agent that ignores the new AGENTS.md paragraph can still one-skill-copy ask-user and get a broken `uv run`. The sidecar plus the procedure are the mitigation; there is no runtime fallback.

## Implementation

### Files

- `ask-user/DEPENDENCIES.md`
- `AGENTS.md`
- `README.md`

### Steps

1. Create `ask-user/DEPENDENCIES.md` as UTF-8 text. Optional `#` comment lines, then a single dependency line `shorten-url`. No other names. No prose paragraph.
2. In `AGENTS.md`, add a Dependencies subsection under Install a skill that defines the format once: ignore empty lines and lines whose first non-space character is `#`; every other line is a sibling directory name. Then: after installing skill `$name`, if `$REPO/$name/DEPENDENCIES.md` exists, install each parsed name that is a repo skill, recursively, skipping names already visited; if a parsed name is not a repo skill, stop and report it. Point both the OpenCode one-skill path and the Agents target at this rule. Do not list `shorten-url` in AGENTS.md.
3. In the OpenCode “Install one skill” sentence, say dest prep, copy that skill, then install its dependencies per the subsection. Leave dest-prep “copy every repo skill” and “update my opencode skills” as they are (they already walk every repo skill).
4. In `README.md`, keep the all-skills symlink loop. Change the one-off example so that after `ln -sfn` of the named skill, the operator also symlinks each name from that skill’s `DEPENDENCIES.md` using the AGENTS.md format (link to AGENTS.md; do not restate `shorten-url` or re-specify the comment syntax).

### Verify

`ask-user/DEPENDENCIES.md` parses to exactly `shorten-url` under the AGENTS.md rules. `rg shorten-url AGENTS.md README.md` does not match an install-dep restatement (mentions inside `ask-user/` and this plan do not count). Reading AGENTS.md is enough to install ask-user and also copy or symlink `shorten-url` without guessing.

## Acceptance

- `ask-user/DEPENDENCIES.md` exists and lists only `shorten-url`.
- AGENTS.md defines the sidecar format and the recurse-and-error procedure.
- OpenCode one-skill install includes dependency install.
- README one-off install includes dependency symlinks and points at AGENTS.md for the format.
- No new parser script or package.
