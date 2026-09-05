**Archive.** Decisions in this file were current as of 2026-09-05 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# ask-user skill

## Goal

Add an `ask-user` skill the agent auto-loads when it needs the user to pick among N options (plus Other) and no questions tool (`ask_user_question` or equivalent) is available. The skill opens a PySide6 wizard, blocks until the user finishes or cancels, and prints machine-readable answers on stdout.

## Settled decisions

Product decisions from the grilling session ([pre_planning_session.md](pre_planning_session.md)):

- **Fallback only.** Prefer the native questions tool when it exists. Load and run this skill only when that tool is absent. Do not dual-fire. Do not replace the native tool when it works.
- **Do not patch consumers in v1.** `grilling`, `create-multi-stage-plan`, `archive-done-plans`, `implement-pending-plans`, `nuclear-review`, and `nuclear-blind-review` already say “questions tool if available.” Leave them alone. Routing is this skill’s catalog description.
- **Match the native contract.** One invocation, N questions. Each question has `question`, `options[{label, description, preview?}]`, optional `multi_select`. The script always appends Other; the agent must not send an Other option. Accept `preview` and ignore it in v1. No extra schema field for “recommended”; the agent puts the recommended option first and the UI marks the first option.
- **Custom PySide6 window**, not Tk, not kdialog/zenity, not chat-only. PySide6 is a uv project dependency of the CLI.
- **Notify-shaped layout in this repo.** `ask-user/SKILL.md` + `uv` CLI at `ask-user/scripts/ask-user`. Same install loop (symlink into `~/.agents/skills/`). No slash-only alias.
- **Name:** `ask-user` (slash `/ask-user`).
- **I/O:** stdin JSON → stdout JSON. No `--file`, no argv payload.
- **Wizard, lenient.** `QWizard`, one question per page. Next always enabled (skip allowed). Back always enabled except on page 1. Finish only on the last page. No page sidebar. Finish with unanswered questions does not close: jump to the first incomplete page and show an inline error. Finish with a complete set → exit 0 + JSON.
- **Window chrome.** Title `ask-user`. Progress `Question N of M`. Raise once on show, then normal stacking. Not always-on-top. Esc / window close / Cancel = cancelled.
- **Other / validity.** Single-select: Other is a radio that enables its text field (xor an option). Multi-select: checkboxes plus Other as extra free text, not exclusive. A page is valid if an option is chosen, or Other is non-empty (multi-select may have labels and Other together).
- **Platforms.** Any OS where Qt can connect to a display. Failure mode is “no display” (exit 4), not “wrong OS.”
- **Failures (Bundle A).** Script has no timeout. Skill tells the agent to block ≥10 minutes. Cancelled and no-display are declines, not crashes; agent falls back to numbered options in chat. Distinct exit codes 0 / 2 / 4 / 6. Do not add a fifth code in v1.
- **Tests.** Contract tests only: JSON validate, Other-append rules, exit codes. Never create a `QApplication`. No GUI / offscreen Qt tests.
- **Description wording** (frontmatter, so agents pick it up when the questions tool is missing):

  > Present multiple-choice questions (N options + Other) in a desktop window when no questions tool is available. Use when you need the user to choose among options and `ask_user_question` / a questions tool is not available. Use when the user runs `/ask-user`.

Implementation-frontier decisions locked for this plan (not reopened):

- **Three modules.** `payload.py` is Qt-free (parse, validate, page completeness, answer encode). `cli.py` owns stdin/stdout, argv, display probe, process exit. `wizard.py` owns `QWizard` only. `cli.py` and `payload.py` must be importable without importing `PySide6`. `wizard.py` is the only module allowed to import Qt.
- **Validation.** Top-level must be a JSON object with a non-empty `questions` array. Extra keys at every level are ignored. `question` is a required string, stripped, non-empty. `options` is a required non-empty array. Each option `label` is a required string, stripped, non-empty. `description` if missing becomes `""`; if present must be a string (empty allowed). `preview` may be any JSON value or absent and is dropped. `multi_select` defaults to false; if present must be a JSON boolean. Duplicate labels inside one question are compared after strip, case-sensitively, and fail. An incoming option whose stripped label is exactly `Other` fails (the script appends Other; the agent must not send it). Duplicate question texts are allowed. There is no max question or option count.
- **Answers.** Same length and order as input questions. `question` is the stripped text. `selected` is the chosen option labels (never `"Other"`). `other` is the stripped free-text or `null`. Compact UTF-8 JSON on stdout (`ensure_ascii=False`, no extra spaces) plus a trailing newline. Nothing else on stdout.
- **Page completeness (shared helper).** A page is complete when `selected` is non-empty or `other` is a non-empty stripped string. Single-select UI enforces at most one label and xor Other; the helper itself is the same for both modes. `first_incomplete` returns the lowest index that fails, or `None`.
- **Display probe.** Before constructing `QApplication`: on Linux, missing/empty `DISPLAY` and `WAYLAND_DISPLAY` is exit 4. Darwin and Windows skip the env check. Then construct `QApplication`; `ImportError` of PySide6, constructor failure, zero screens, or platform name `offscreen` / `minimal` is exit 4 with a stderr line. Missing Qt is “cannot open a window,” not a new exit code.
- **Wizard chrome (implementation).** `QWizard.ClassicStyle`. Options: `IndependentPages`, `NoBackButtonOnStartPage`, no help button, Cancel kept, no Next on last page, no Finish on early pages. Each page’s `isComplete()` is always `True` so Next is never greyed. Whole-set validation runs only when Finish is clicked (`validateCurrentPage` on the last page): if any page is incomplete, jump there, show the inline error `This question needs an answer.`, and refuse to close. No option is pre-selected. First option gets a sibling `Recommended` badge `QLabel`; the radio/checkbox text stays the raw label so answers do not contain the badge. Option descriptions render as secondary wrapped labels; an empty description adds no extra widget.
- **Other row.** Visible label `Other`. Single-select: `QRadioButton` in the same `QButtonGroup` as the options, plus a `QLineEdit` enabled only while Other is checked. Multi-select: `QCheckBox` plus a `QLineEdit` enabled only while that box is checked; option boxes stay independent. Collected `other` is the stripped line-edit text only when Other is checked and the text is non-empty; otherwise `null`. Typing then unchecking Other drops the text from the answer.
- **CLI argv.** No payload flags. Unknown positional or optional args are exit 2. `-h` / `--help` may exit 0 via argparse. Payload is stdin only, UTF-8.
- **Packaging.** Same uv_build + src layout as `notify`. Project name `ask-user`, package `ask_user`, console script `ask-user = "ask_user.cli:main"`. `requires-python = ">=3.10,<3.15"`. Runtime dependency `PySide6` (unpinned in `pyproject.toml`; `uv.lock` pins). Dev dependency-group `pytest`. Commit `uv.lock`.
- **Docs split.** `SKILL.md` is the only agent contract: when to fire, invoke line, ≥10 minute block (600000 ms if the tool uses milliseconds), JSON shapes, exit table, fallback on 4 and 6, pointer at `README.md`. `README.md` is the only first-run home: PySide6 wheel download, display / Wayland, human smoke test. No repo-root `README.md` / `AGENTS.md` edit. No ADR.

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

**Process order.** Read stdin → parse/validate (exit 2, no window) → Linux display-env probe (exit 4) → construct `QApplication` (failure → exit 4) → run the wizard → cancel/close/Esc → exit 6 with no stdout JSON → success → print answers JSON, exit 0.

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

`multi_select` defaults to false. `preview` on an option is allowed and ignored. Zero questions, invalid JSON, or duplicate labels inside one question → exit 2 before the window opens. Full reject list is under Settled decisions.

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
| 2 | usage / invalid JSON / empty questions / duplicate labels / reserved `Other` label / extra argv |
| 4 | no display (env, Qt cannot connect, or PySide6 missing) |
| 6 | cancelled (close / Esc / Cancel) |

Errors go to stderr.

### Window

PySide6 `QWizard` as specified under Settled decisions. One question per page. Recommended badge on the first option. Other row as specified. Submit/Finish stays on the last page; validation of the whole set happens there. Application name is `ask-user` (Wayland/app class). Minimum size 520×400. No `WindowStaysOnTopHint`. After `show()`, call `raise_()` and `activateWindow()` once.

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
        payload.py
        cli.py
        wizard.py
      tests/
        test_payload.py
        test_cli.py
```

- `SKILL.md` stays thin: when to fire, invoke line, timeout, exit codes, JSON shape, fall-back-on-4-and-6. Pointer at `README.md` on failure.
- `README.md` is the only home for first-run notes (PySide6 wheel download, display/Wayland, human smoke test).

### Tests

Pytest against `payload` and `cli` only. CLI tests monkeypatch the display probe and `run_wizard`; they never construct a `QApplication`. `wizard.py` has no pytest. A test asserts that importing `ask_user.payload` and `ask_user.cli` does not import `PySide6`.

## Stage map

1. **Payload + uv project** — the JSON contract is the shared language for the CLI, the wizard, and the tests. Nothing else can be written until parse/validate/encode and page-completeness exist, and the uv project is the home those modules live in. No Qt in this stage, so the contract is testable in a headless agent shell.
2. **CLI I/O** — depends on the payload types and error class. Locks stdin/stdout, argv, the exit table, and the display probe. The wizard is an injectable hook (stub module) so exit-code tests do not need a window.
3. **Wizard** — depends on payload helpers for completeness and on the CLI hook from stage 02. Replaces the stub with the real `QWizard`. Last because it is the only Qt surface and is verified by reading the code plus a human smoke path, not pytest.
4. **Skill + README** — describe the invoke line, timeout, JSON, and exits only after those exist. Skill and README ship together so the failure pointer has a real target and first-run text is not stuffed into the skill.

## Out of scope

- Patching grilling or other “questions tool if available” skills
- Rendering `preview`
- Tk, kdialog, zenity, HTML, or terminal pickers
- Always-on-top, page sidebar, wizard self-timeout
- Slash-only alias (`ask-user-me` or similar)
- A fifth exit code, `--file`, or argv payload
- GUI / offscreen Qt tests, or any test that constructs `QApplication`
- Repo-root `README.md` or `AGENTS.md` edits
- An ADR

## Assumptions

- `uv` is on machines that implement and use the skill.
- After the files exist, install is the existing per-skill symlink loop in the repo `README.md`.
- The host has a graphical session when the window should appear (`DISPLAY` / `WAYLAND_DISPLAY`). This machine is Plasma on Wayland; Tk was not importable (`libtk8.6.so` missing); that is why Qt was chosen, not Tk.
- Agents see skill descriptions in their catalog and will load `ask-user` from the wording above when a questions tool is missing. If that fails in practice, patching consumers is a later change.
- Default agent command timeout (~120s) will background a modal unless the skill forces a long block.
- Skill-design-principles apply: one home per fact, thin `SKILL.md`, first-run notes only in `README.md`.
- PySide6 6.11.x requires Python `>=3.10,<3.15`; the project bound matches that, which includes the 3.14 interpreter on this machine.
