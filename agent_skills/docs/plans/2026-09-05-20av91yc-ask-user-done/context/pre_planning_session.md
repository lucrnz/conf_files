# ask-user skill

Grilling-session capture that settled the product decisions. The plan-authoritative expansion is [design.md](design.md). Not living documentation.

## Goal

Add an `ask-user` skill the agent auto-loads when it needs the user to pick among N options (plus Other) and no questions tool (`ask_user_question` or equivalent) is available. The skill opens a PySide6 wizard, blocks until the user finishes or cancels, and prints machine-readable answers on stdout.

## Settled decisions

- **Fallback only.** Prefer the native questions tool when it exists. Load and run this skill only when that tool is absent. Do not dual-fire. Do not replace the native tool when it works.
- **Do not patch consumers in v1.** `grilling`, `create-multi-stage-plan`, `archive-done-plans`, `implement-pending-plans`, `nuclear-review`, and `nuclear-blind-review` already say “questions tool if available.” Leave them alone. Routing is this skill’s catalog description.
- **Match the native contract.** One invocation, N questions. Each question has `question`, `options[{label, description, preview?}]`, optional `multi_select`. The script always appends Other; the agent must not send an Other option. Accept `preview` and ignore it in v1. No extra schema field for “recommended”; the agent puts the recommended option first and the UI marks the first option.
- **Custom PySide6 window**, not Tk, not kdialog/zenity, not chat-only. PySide6 is a uv project dependency of the CLI.
- **Notify-shaped layout in this repo.** `ask-user/SKILL.md` + `uv` CLI at `ask-user/scripts/ask-user`. Same install loop (symlink into `~/.agents/skills/`). No slash-only alias.
- **Name:** `ask-user` (slash `/ask-user`).
- **I/O:** stdin JSON → stdout JSON. No `--file`, no argv payload.
- **Wizard, lenient.** `QWizard`, one question per page. Next always enabled (skip allowed). Back always enabled except on page 1. Finish only on the last page. No page sidebar. Finish with unanswered questions does not close: jump to the first incomplete page and show an inline error. Finish with a complete set → exit 0 + JSON.
- **Window chrome.** Title `ask-user`. Progress `Question N of M`. Raise once on show, then normal stacking. Not always-on-top. Esc / window close = cancelled.
- **Other / validity.** Single-select: Other is a radio that enables its text field (xor an option). Multi-select: checkboxes plus Other as extra free text, not exclusive. A page is valid if an option is chosen, or Other is non-empty (multi-select may have labels and Other together).
- **Platforms.** Any OS where Qt can connect to a display. Failure mode is “no display” (exit 4), not “wrong OS.”
- **Failures (Bundle A).** Script has no timeout. Skill tells the agent to block ≥10 minutes. Cancelled and no-display are declines, not crashes; agent falls back to numbered options in chat. Distinct exit codes (table below).
- **Tests.** Contract tests only: JSON validate, Other-append, exit codes. Never create a `QApplication`. No GUI / offscreen Qt tests.
- **Description wording** (frontmatter, so agents pick it up when the questions tool is missing):

  > Present multiple-choice questions (N options + Other) in a desktop window when no questions tool is available. Use when you need the user to choose among options and `ask_user_question` / a questions tool is not available. Use when the user runs `/ask-user`.

## Design

`ask-user` is the agent contract. The CLI is the only process that talks to Qt.

### When to fire

The skill has no `disable-model-invocation`. The description lists the questions-tool-missing trigger and `/ask-user`. The agent already printed (or will print) questions in chat if the calling skill says so; the window is still self-contained (full question text + option labels and descriptions) because not every caller prints first.

On CLI exit 4 or 6: fall back to numbered options in chat. Do not retry the window. On exit 2: report stderr, do not retry.

### CLI

Resolve the directory that contains this `SKILL.md` (follow the symlink if reached via `~/.agents/skills/ask-user`). Then:

```
uv run --project <that-dir>/scripts/ask-user ask-user
```

Never invoke with a cwd-relative `ask-user/scripts/ask-user` path. Feed the payload on stdin. Agent must set the shell-tool timeout to at least 10 minutes so the modal is not backgrounded.

**Input** (native shape):

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

`multi_select` defaults to false. `preview` on an option is allowed and ignored. Zero questions, invalid JSON, or duplicate labels inside one question → exit 2 before the window opens.

**Output** (stdout on success only; nothing else on stdout):

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

`selected` is option labels (zero or more). `other` is the free-text string or `null`. Multi-select may have several labels and a non-null `other`.

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | success, JSON answers on stdout |
| 2 | usage / invalid JSON / empty questions / duplicate labels |
| 4 | no display (Qt cannot connect) |
| 6 | cancelled (close / Esc) |

Errors go to stderr.

### Window

PySide6 `QWizard`. One question per page. Recommended badge on the first option. Other row as specified above. Submit/Finish stays on the last page; validation of the whole set happens there.

### Packaging

Same shape as `notify`:

```
ask-user/
  SKILL.md
  README.md
  scripts/
    ask-user/
      pyproject.toml
      uv.lock
      src/ask_user/
        __init__.py
        cli.py
        …
      tests/
```

- `requires-python` compatible with PySide6 (`>=3.10,<3.15` as of PySide6 6.11.2).
- Runtime dependency: `PySide6`.
- Console script: `ask-user = "ask_user.cli:main"`.
- `SKILL.md` stays thin: when to fire, invoke line, timeout, exit codes, JSON shape, fall-back-on-4-and-6. Pointer at `README.md` on failure.
- `README.md` is the only home for first-run notes (PySide6 wheel download, display/Wayland, human smoke test).

### Tests

Pytest against validate/parse/exit helpers only. No `QApplication`.

## Out of scope

- Patching grilling or other “questions tool if available” skills
- Rendering `preview`
- Tk, kdialog, zenity, HTML, or terminal pickers
- Always-on-top, page sidebar, wizard self-timeout
- Slash-only alias (`ask-user-me` or similar)
- Repo-root `README.md` or `AGENTS.md` edits
- An ADR

## Assumptions

- `uv` is on machines that implement and use the skill.
- After the files exist, install is the existing per-skill symlink loop in the repo `README.md`.
- The host has a graphical session when the window should appear (`DISPLAY` / `WAYLAND_DISPLAY`). This machine is Plasma on Wayland; Tk was not importable (`libtk8.6.so` missing); that is why Qt was chosen, not Tk.
- Agents see skill descriptions in their catalog and will load `ask-user` from the wording above when a questions tool is missing. If that fails in practice, patching consumers is a later change.
- Default agent command timeout (~120s) will background a modal unless the skill forces a long block.

## Environment facts (from the grilling session)

- OS session: Linux, Plasma, Wayland (`DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`).
- Python 3.14.7. PySide6 latest at session time: 6.11.2, `requires_python >=3.10,<3.15`.
- Agent shell is not a TTY; terminal UIs (`fzf`, `whiptail`) launched by the agent are unusable.
- Present and unused for v1: `kdialog`, `zenity`, `notify-send`.
- Closest existing skill: `notify` (thin `SKILL.md`, `uv` CLI, OS helper). Notify is fire-and-forget; this skill is a blocking modal.
