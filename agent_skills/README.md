# Agent skills

Shared skills for coding agents (one directory per skill, each with a `SKILL.md`).

## Install

Symlink each skill into `~/.agents/skills/`. Prefer per-skill links over linking this whole directory, so you can still add local-only skills beside them.

```bash
mkdir -p ~/.agents/skills
REPO_SKILLS="$HOME/.conf_files/agent_skills"  # or path to this clone

for skill in "$REPO_SKILLS"/*/; do
  name=$(basename "$skill")
  [ -f "$skill/SKILL.md" ] || continue
  ln -sfn "$REPO_SKILLS/$name" "$HOME/.agents/skills/$name"
done
```

One-off:

```bash
ln -sfn /path/to/agent_skills/deslop ~/.agents/skills/deslop
```

Check with `ls -la ~/.agents/skills/`.
