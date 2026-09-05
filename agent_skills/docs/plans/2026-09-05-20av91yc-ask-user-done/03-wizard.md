# Stage 03: Wizard

## Status
done

## Description

Replace the stub with a PySide6 `QWizard`: one question per page, recommended badge, Other row, lenient Next/Back, and Finish-time whole-set validation.

## Rationale

The CLI already knows how to open a session and how to turn `Answer` values into stdout. This stage is the only Qt surface; keeping it in one file means contract tests stay Qt-free.

## Invariants

- Only `wizard.py` imports PySide6 / Qt. Do not add Qt imports to `payload.py` or to the module-level of `cli.py`.
- Next is always enabled (page `isComplete()` is always `True`). Finish is only on the last page. Back is hidden on page 1.
- No option is pre-selected. The first option’s returned label is the raw label, never a string that includes `Recommended`.
- Cancel, Esc, and window close all map to `run_wizard` returning `None` (CLI exit 6). Success returns one `Answer` per question, same order.
- No pytest in this stage. Do not construct a `QApplication` under tests.

## Risks

A first-run `uv` resolve will download the PySide6 wheel, which is large and needs a graphical session to actually show a window. That is a README concern in stage 04, not a reason to add an offscreen test here. Finish-with-skips is the easy bug: if `validateCurrentPage` only checks the current page, unanswered earlier pages will leak through.

## Implementation

### Files

- `ask-user/scripts/ask-user/src/ask_user/wizard.py`

### Steps

1. Replace `ask-user/scripts/ask-user/src/ask_user/wizard.py` with a real `run_wizard(payload) -> list[Answer] | None` that assumes a `QApplication` already exists (stage 02 constructed it). Do not create a second `QApplication`.
2. In that same file, build a `QWizard` with window title `ask-user`, application-visible name already set by the CLI, `ClassicStyle`, `IndependentPages`, `NoBackButtonOnStartPage`, help button off, Cancel on, no Next on the last page, no Finish on early pages. Minimum size 520×400. Do not set `WindowStaysOnTopHint`. After `show()`, call `raise_()` and `activateWindow()` once, then `exec()`.
3. In that same file, add one page per question. Page title or subtitle is `Question N of M` (1-based). Question text is a word-wrapped `QLabel`. Single-select: `QRadioButton` per option in one `QButtonGroup`. Multi-select: `QCheckBox` per option. Next to the first option only, a sibling `QLabel` with text `Recommended` (not part of the button text). Each non-empty description is a secondary wrapped `QLabel` under that option; empty description adds no widget.
4. In that same file, append the Other row on every page: label text `Other`. Single-select: `QRadioButton` in the same group plus a `QLineEdit` enabled only while Other is checked. Multi-select: `QCheckBox` plus a `QLineEdit` enabled only while that box is checked; option boxes stay independent. No option and not Other is the initial state.
5. In that same file, collect answers with the completeness rules in [context/design.md](context/design.md): `selected` is the checked option labels (never `Other`); `other` is the stripped line-edit text only when Other is checked and the text is non-empty, else `null`. Use `page_complete` / `first_incomplete` from the payload module. Each page keeps a hidden inline error `QLabel` whose text is `This question needs an answer.`
6. In that same file, keep each page’s `isComplete()` returning `True` so Next is never greyed. On Finish, the last page’s `validateCurrentPage` runs `first_incomplete` over every page: if an index is returned, `setCurrentId` to that page, show that page’s inline error, and return `False`. If every page is complete, return `True` and let the wizard accept. `run_wizard` then builds the `Answer` list. Reject / Cancel / close → return `None`.

### Verify

- Read `ask-user/scripts/ask-user/src/ask_user/wizard.py` and confirm: `ClassicStyle`; `IndependentPages`; `NoBackButtonOnStartPage`; `isComplete()` always `True`; Finish validation uses `first_incomplete` and the exact error string; first option badge is a sibling label; Other is appended in the UI and never appears in `selected`; no `WindowStaysOnTopHint`; `raise_()` / `activateWindow()` once after `show()`; no second `QApplication`.
- `rg -n "PySide6|from PySide6|import Qt" ask-user/scripts/ask-user/src/ask_user/payload.py ask-user/scripts/ask-user/src/ask_user/cli.py` — `payload.py` has no matches; `cli.py` matches only inside `ensure_application` (or an equivalently lazy helper), not at module top.
- `uv run --project ask-user/scripts/ask-user --group dev pytest ask-user/scripts/ask-user/tests` still exits 0 (existing tests, no new GUI tests).
- Do not open the wizard as part of automated verify. A human smoke command belongs in stage 04’s README.

## Acceptance

- `run_wizard` returns answers that satisfy the output contract, or `None` on cancel/close/Esc.
- Next never blocks on an unanswered page; Finish refuses a partial set by jumping to the first incomplete page and showing the inline error.
- No GUI tests were added. `payload.py` remains Qt-free.
