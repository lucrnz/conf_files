# Stage 01: Payload contract

## Status
done

## Description

Create the uv project and the Qt-free payload module: parse and validate the native questions JSON, encode answers, and expose the page-completeness helpers the wizard will call.

## Rationale

CLI, wizard, and tests all speak this contract. Locking it first — without importing Qt — freezes the reject list and the answer shape so later stages do not invent a parallel schema.

## Invariants

- `payload.py` must not import `PySide6` or any `Qt*` module.
- Incoming option label `Other` (exact, after strip) is a validation error. The script appends Other later; this stage only rejects the reserved label.
- Extra JSON keys at every level are ignored. `preview` is dropped.

## Risks

A loose parser that accepts a missing `options` key or a non-bool `multi_select` will let bad payloads reach the window in later stages. The reject list in [context/design.md](context/design.md) is closed; do not add a “best effort” path.

## Implementation

### Files

- `ask-user/scripts/ask-user/pyproject.toml`
- `ask-user/scripts/ask-user/uv.lock`
- `ask-user/scripts/ask-user/src/ask_user/__init__.py`
- `ask-user/scripts/ask-user/src/ask_user/payload.py`
- `ask-user/scripts/ask-user/tests/test_payload.py`

### Steps

1. Write `ask-user/scripts/ask-user/pyproject.toml` the same way as the other uv console-script projects in this repo: `uv_build`, module `ask_user` under `src`, console script `ask-user = "ask_user.cli:main"`, `requires-python = ">=3.10,<3.15"`, runtime dependency `PySide6`, `[dependency-groups] dev = ["pytest"]`, and `[tool.pytest.ini_options] testpaths = ["tests"]`. Do not pin a PySide6 version in `pyproject.toml`.
2. Write `ask-user/scripts/ask-user/src/ask_user/__init__.py` (empty or a one-line package docstring).
3. Write `ask-user/scripts/ask-user/src/ask_user/payload.py` with frozen dataclasses `Option` (`label`, `description`), `Question` (`question`, `options` tuple, `multi_select`), `Payload` (`questions` tuple), `Answer` (`question`, `selected` tuple, `other` `str | None`), and a `PayloadError` exception whose message is safe to print on stderr.
4. In that same file, implement `loads(text: str) -> Payload` (JSON decode, then validate) and `parse_payload(data: object) -> Payload` matching the reject list in [context/design.md](context/design.md): top-level object with a non-empty `questions` array; each `question` a stripped non-empty string; `options` a non-empty array; each `label` a stripped non-empty string; `description` missing → `""`, present non-string → error; `preview` any type or absent, dropped; `multi_select` missing → false, present non-bool → error; extra keys ignored; duplicate labels after strip, case-sensitive, error; stripped label exactly `Other` → error. Invalid JSON raises `PayloadError`.
5. In that same file, implement `page_complete(selected: Sequence[str], other: str | None) -> bool` (complete when `selected` is non-empty or stripped `other` is non-empty), `first_incomplete(pages: Sequence[tuple[Sequence[str], str | None]]) -> int | None`, and `encode_answers(answers: Sequence[Answer]) -> str` as compact UTF-8 JSON (`ensure_ascii=False`, no extra spaces) of `{"answers":[...]}` plus a trailing newline. `other` is `null` when unused.
6. Write `ask-user/scripts/ask-user/tests/test_payload.py` covering: a valid single-select payload; a valid multi-select payload; `preview` and extra keys ignored; empty stdin-equivalent / invalid JSON / non-object / missing or empty `questions`; whitespace-only question; empty `options`; empty label; duplicate labels; reserved `Other` label; non-bool `multi_select`; `page_complete` / `first_incomplete`; `encode_answers` shape and compact separators; importing `ask_user.payload` does not import `PySide6`.
7. Generate `ask-user/scripts/ask-user/uv.lock` with `uv lock` so it is committed. The lock will include PySide6 even though this stage never imports it.

### Verify

- `uv run --project ask-user/scripts/ask-user --group dev pytest ask-user/scripts/ask-user/tests/test_payload.py` exits 0.
- Read `ask-user/scripts/ask-user/src/ask_user/payload.py` and confirm there is no `PySide6` / `Qt` import and that reserved `Other`, duplicate labels, and empty `questions` all raise `PayloadError`.
- Read `ask-user/scripts/ask-user/pyproject.toml` and confirm `requires-python = ">=3.10,<3.15"`, runtime `PySide6`, console script `ask-user = "ask_user.cli:main"`, and a `dev` pytest group.
- Confirm `ask-user/scripts/ask-user/uv.lock` exists and lists PySide6.

## Acceptance

- A valid native-shaped JSON object becomes a `Payload`; every reject case in [context/design.md](context/design.md) raises `PayloadError` before any window exists.
- `encode_answers` prints only the compact `answers` document plus a newline.
- `payload.py` and its tests never import Qt. The uv project is lockable and names the `ask-user` console script even though `cli.py` is not in this stage.
