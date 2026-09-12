# Stage 01: v.gd client

## Status
done

## Description

Add a Qt-free `ask_user.shorten` module that POSTs a URL to v.gd’s create API, returns a validated `https://v.gd/…` string, retries once on transient failure, and returns `None` otherwise. CLI print behaviour does not change in this stage.

## Rationale

The POST / parse / retry rules can be pinned with a fake `urlopen` before `run_ssh_picker` starts depending on them. Wiring first would leave the failure matrix untested or force it into CLI tests.

## Invariants

- No new package dependency. `urllib.request` only.
- Importing `ask_user.shorten` does not import `PySide6`.
- `shorten` does not print, log, or raise on v.gd / network failure; it returns `str | None`.
- No `shorturl`, `logstats`, or `callback` parameter is sent.
- Tests never open a real socket to v.gd.

## Risks

v.gd’s simple format puts errors in the body with varying HTTP codes. Using `format=json` avoids treating an `Error: …` line as a short URL. Do not parse `format=simple`.

## Implementation

### Files

- `ask-user/scripts/ask-user/src/ask_user/shorten.py`
- `ask-user/scripts/ask-user/tests/test_shorten.py`

### Steps

1. Write `ask-user/scripts/ask-user/src/ask_user/shorten.py` with `CREATE_URL = "https://v.gd/create.php"`, `SHORTEN_TIMEOUT_SECS = 5.0`, and `shorten(url: str) -> str | None` as specified in [context/design.md](context/design.md): POST form fields `format=json` and `url`; header `User-Agent: ask-user`; `timeout=SHORTEN_TIMEOUT_SECS`. Parse JSON. On `shorturl`, rewrite `http://v.gd/` to `https://v.gd/`, then accept only a single-line `https://v.gd/` URL with a non-empty path and no whitespace. Retry immediately once on timeout, `URLError`, HTTP 5xx, v.gd error codes 3 and 4, and JSON / shape / validation failure. Return `None` immediately (no retry) on HTTP 400, HTTP 406, and v.gd error codes 1 and 2. Do not import Qt.
2. Write `ask-user/scripts/ask-user/tests/test_shorten.py` that patches `urllib.request.urlopen` (or the module attribute `shorten` uses). Cover: 200 + `{"shorturl":"https://v.gd/R709K6"}` returns that URL and one call; `http://v.gd/R709K6` is rewritten to `https://v.gd/R709K6`; a first `URLError` / timeout then a valid body returns the short URL and two calls; two failures return `None`; HTTP 400 / JSON error code 1 returns `None` after one call; HTTP 502 then success retries; a 200 body that is not a v.gd URL returns `None` after the retry; the POST target is `https://v.gd/create.php`, the body includes `format=json` and a URL-encoded `url=`, and `shorturl` / `logstats` are absent; importing `ask_user.shorten` does not import `PySide6`.

### Verify

- `uv run --project ask-user/scripts/ask-user --group dev pytest ask-user/scripts/ask-user/tests/test_shorten.py` exits 0.
- Read `ask-user/scripts/ask-user/src/ask_user/shorten.py` and confirm `CREATE_URL` is `https://v.gd/create.php`, `format=json`, no `shorturl` / `logstats`, timeout 5.0, and no Qt import.
- `rg "ask-user:" ask-user/scripts/ask-user/src/ask_user/cli.py` still prints `{public}` (the long URL). This stage does not edit `cli.py`.

## Acceptance

- `shorten("https://example.trycloudflare.com/t/<64-hex>/")` returns `https://v.gd/…` when the mocked API succeeds, including after one transient failure.
- `shorten` returns `None` after two transient failures, and after a single error-code-1 response.
- Pytest does not contact v.gd.
