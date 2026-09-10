# Agent instructions

This file is for agents working in this repo. `REPO` is the directory that contains this file.

## Author a skill

When writing or editing a skill, it should be compatible with Linux and macOS unless it cannot make sense on both.

## Install a skill

If the user already names a target (`for opencode`, `update my opencode skills`, agents/symlink, etc.), use that target. Do not ask again.

If they say "install \<skill\>" and do **not** name a target:

1. Follow `ask-user/SKILL.md` in this repo. Run it from this repo even if ask-user is not installed for the current agent.
2. Ask with these options, recommended first: **Both**, **Agents** (symlinks), **OpenCode** (hard copy).
3. Do the matching steps below. **Both** means Agents then OpenCode.

### Agents (`~/.agents/skills`)

Follow `./README.md`.

### OpenCode (`~/.config/opencode/skills`)

Hard-copy only. Never symlink. Never write through a symlink into this repo.

A **repo skill** is a child directory of `REPO` that contains `SKILL.md`.

**Dest prep.** `DEST="$HOME/.config/opencode/skills"`.

- If `DEST` is a symlink: unlink the symlink only (`rm` the link, do not follow it, do not `rm -rf` this repo), then `mkdir -p "$DEST"`. That is a **first OpenCode write**: immediately copy **every** repo skill (see Copy below), then continue with the named skill if one was requested.
- If `DEST` does not exist: `mkdir -p "$DEST"`.
- If `DEST` is a real directory: leave it.

**Copy** skill `$name` so dest matches source. If `"$DEST/$name"` is a symlink, unlink it first. Exclude `__pycache__`, `*.pyc`, and `.DS_Store`. Delete extra files inside that dest skill directory.

```bash
rsync -a --delete \
  --exclude '__pycache__' --exclude '*.pyc' --exclude '.DS_Store' \
  "$REPO/$name/" "$DEST/$name/"
```

**Install one skill for OpenCode:** dest prep, then copy that skill. (A first write already seeded every repo skill.)

**"update my opencode skills":** dest prep, then for every repo skill compare dest to source (`diff -rq` with the same excludes, or `rsync -n`). If the dest skill is missing or files differ, copy as above. Leave dest-only skills (directories in `DEST` that are not repo skills) alone.

Do not install or update OpenCode copies unless the user asked.
