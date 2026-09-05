---
name: ask-user
description: Present multiple-choice questions (N options + Other) in a desktop window when no questions tool is available. Use when you need the user to choose among options and `ask_user_question` / a questions tool is not available. Use when the user runs `/ask-user`.
---

# ask-user

Prefer the native questions tool when it exists. Load this skill only when it does not. Do not dual-fire.

The window is self-contained: full question text, option labels, and descriptions. Do not send an Other option; the CLI appends it. Put the recommended option first.

## Mechanical CLI

This skill lives in the directory that contains this `SKILL.md`. Follow the symlink if you reached it via `~/.agents/skills/ask-user`. Resolve that directory, then:

```
uv run --project <that-dir>/scripts/ask-user ask-user
```

Never invoke with a cwd-relative `ask-user/scripts/ask-user` path. Feed the JSON payload on stdin.

Set the shell/command tool timeout to at least 10 minutes (600000 ms if the tool uses milliseconds) so the process is not backgrounded. The CLI itself has no timeout.

## Input (stdin)

```json
{
  "questions": [
    {
      "question": "When does the agent use this?",
      "options": [
        {"label": "Fallback only", "description": "Native tool when present."},
        {"label": "Always this skill", "description": "Ignore the native tool."}
      ],
      "multi_select": false
    }
  ]
}
```

`multi_select` defaults to false. `preview` on an option is allowed and ignored.

## Output (stdout, exit 0 only)

```json
{
  "answers": [
    {
      "question": "When does the agent use this?",
      "selected": ["Fallback only"],
      "other": null
    }
  ]
}
```

`selected` is option labels. `other` is the free-text string or `null`. Multi-select may have several labels and a non-null `other`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success, JSON answers on stdout |
| 2 | usage / invalid JSON / empty questions / duplicate labels / reserved Other / extra argv |
| 4 | no display |
| 6 | cancelled (close / Esc / Cancel) |

Exit 4 or 6: fall back to numbered options in chat. Do not retry the window. Exit 2: report stderr, do not retry.

If the CLI exits non-zero: point the user at [README.md](README.md) in this skill directory.
