---
name: ask-user
description: Present multiple-choice questions (N options + Other) in a desktop window, or a tunneled browser page over SSH. Use when you need the user to choose among options. Replaces `ask_user_question` / a questions tool; fall back to that tool only if this picker cannot open. Use when the user runs `/ask-user`.
---

# ask-user

Always use this skill when a pick is needed. It replaces `ask_user_question` / a questions tool. Do not dual-fire.

The picker is self-contained: full question text, option labels, and descriptions. Do not send an Other option; the CLI appends it. Put the recommended option first.

## Mechanical CLI

This skill lives in the directory that contains this `SKILL.md`. Follow the symlink if you reached it via `~/.agents/skills/ask-user`. Resolve that directory, then:

```
uv run --project <that-dir>/scripts/ask-user ask-user
```

Never invoke with a cwd-relative `ask-user/scripts/ask-user` path. Feed the JSON payload on stdin.

The CLI auto-detects SSH (`SSH_CONNECTION`, `SSH_CLIENT`, or `SSH_TTY` in the command environment) and does not open a desktop window then. Do not pass flags to choose a backend.

If that environment has a non-empty `SSH_CONNECTION`, `SSH_CLIENT`, or `SSH_TTY`, set the shell/command tool timeout to at least 4 hours (14400000 ms if the tool uses milliseconds). Otherwise set it to at least 10 minutes (600000 ms). The CLI waits 10 minutes for the tunneled page to be opened; after that beacon it does not time out.

As soon as stderr contains a line starting with `ask-user: `, print the rest of that line to the user immediately and keep waiting. That line is the wizard URL, not the answers JSON.

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
| 4 | picker could not be presented (no display, no tunnel, or the URL was never opened) |
| 6 | cancelled (close / Esc / Cancel) |

Cannot-open (exit 4, or the CLI never starts: uv/Qt fail, timeout, missing skill): if a questions tool exists, use it now. Else numbered options in chat. Do not retry the picker.

Exit 6: decline. Do not fall back to the questions tool. The caller keeps its decline rule.

Exit 2: report stderr, do not retry.

If the CLI exits non-zero: point the user at [README.md](README.md) in this skill directory.
