# Stage 01: Bump unused fuse to 40 minutes

## Status
done

## Description

Change the SSH unused-fuse default from 10 minutes to 40 minutes, pin that default in the existing import test, and update the SKILL.md sentence that documents the wait-for-open.

## Rationale

The default lives in one constant. Updating the constant without the test pin and the agent-facing sentence leaves a lying contract.

## Invariants

- After `/opened`, the picker still does not time out.
- Unused fire still raises `UnusedTimeout` and the CLI still exits 4 with `not opened`.
- Tests that pass `unused_timeout_secs=0.05` keep using that short override.
- The SKILL.md desktop tool-timeout sentence (“at least 10 minutes (600000 ms)”) and the SSH 4-hour tool-timeout sentence stay as they are.

## Risks

None

## Implementation

### Files

- `ask-user/scripts/ask-user/src/ask_user/http_wizard.py`
- `ask-user/scripts/ask-user/tests/test_http_wizard.py`
- `ask-user/SKILL.md`

### Steps

1. In `ask-user/scripts/ask-user/src/ask_user/http_wizard.py`, set `DEFAULT_UNUSED_TIMEOUT_SECS = 2400.0`. Do not change `HttpPicker` construction, `_on_unused`, or `_mark_opened`.
2. In `ask-user/scripts/ask-user/tests/test_http_wizard.py`, change `assert http_mod.DEFAULT_UNUSED_TIMEOUT_SECS == 600.0` to `== 2400.0`. Leave `test_unused_timeout_without_opened` and `test_opened_then_short_interval_does_not_fire` on `unused_timeout_secs=0.05`.
3. In `ask-user/SKILL.md`, change only “The CLI waits 10 minutes for the tunneled page to be opened” to “The CLI waits 40 minutes for the tunneled page to be opened”. Do not edit the “at least 10 minutes (600000 ms)” desktop tool-timeout clause on that same line.

### Verify

From the repo root:

```
uv run --project ask-user/scripts/ask-user --group dev pytest
```

All existing tests pass. `rg 'DEFAULT_UNUSED_TIMEOUT_SECS|waits 10 minutes for the tunneled'` shows `2400.0` in `http_wizard.py` and `test_http_wizard.py`, and no remaining “waits 10 minutes for the tunneled” in `ask-user/SKILL.md`.

## Acceptance

- `DEFAULT_UNUSED_TIMEOUT_SECS` is `2400.0`.
- The import test asserts `2400.0`.
- SKILL.md says the CLI waits 40 minutes for the tunneled page to be opened, and still says the non-SSH agent tool timeout is at least 10 minutes.
- `uv run --project ask-user/scripts/ask-user --group dev pytest` exits 0.
