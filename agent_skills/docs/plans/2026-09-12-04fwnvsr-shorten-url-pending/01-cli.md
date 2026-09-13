# Stage 01: CLI

## Status
pending

## Description

Add the `uv` project that takes `--url`, pass-throughs an existing v.gd link, or POSTs to v.gd and prints one `https://v.gd/…` URL, using the wire, retry, log, and exit contract in [context/design.md](context/design.md).

## Rationale

The skill can only shell out. Locking the invoke line, flags, pass-through, and failure codes first freezes what `SKILL.md` will document.

## Invariants

- No runtime Python dependencies. `requires-python` is `>=3.11`.
- The only flag is `--url`. It is required; empty or whitespace-only is usage failure.
- No `tests/` directory, no pytest extra, no `--dry-run`.
- No `shorturl`, `logstats`, or `callback` field is sent.
- Verify never opens a real socket to v.gd.

## Risks

A verify step that passes a non-v.gd `http(s)` URL will hit the live API. Usage and pass-through cases are the only safe automated checks; the retry matrix is confirmed by reading the client.

## Implementation

### Files

- `shorten-url/scripts/shorten-url/`
- `shorten-url/scripts/shorten-url/pyproject.toml`
- `shorten-url/scripts/shorten-url/uv.lock`
- `shorten-url/scripts/shorten-url/src/shorten_url/__init__.py`
- `shorten-url/scripts/shorten-url/src/shorten_url/cli.py`
- `shorten-url/scripts/shorten-url/src/shorten_url/client.py`

### Steps

1. Write `shorten-url/scripts/shorten-url/pyproject.toml` the same way as the other uv console-script projects in this repo: `uv_build`, module `shorten_url` under `src`, console script `shorten-url = "shorten_url.cli:main"`, `requires-python = ">=3.11"`, no runtime `dependencies`, no `dev` pytest extra.
2. Write `shorten-url/scripts/shorten-url/src/shorten_url/__init__.py` (empty or a one-line package docstring).
3. Write `shorten-url/scripts/shorten-url/src/shorten_url/cli.py` with argparse: required `--url`, `prog="shorten-url"`. Extra positional argv is usage failure. Strip `--url`; if it is empty or still contains whitespace, print a usage error to stderr and return `2`. If the scheme is not `http` or `https` (case-insensitive), return `2` without calling v.gd. If the host is `v.gd` (case-insensitive) and the path has a nonempty code, print `https://v.gd/` plus that path/query/fragment and return `0`. Otherwise call `shorten` from `shorten_url.client`: a returned string is printed as one stdout line and the process returns `0`; `None` returns `4` (the client already logged).
4. Write `shorten-url/scripts/shorten-url/src/shorten_url/client.py` as specified in [context/design.md](context/design.md): `CREATE_URL = "https://v.gd/create.php"`, `SHORTEN_TIMEOUT_SECS = 5.0`, `RATE_LIMIT_WAIT_SECS = 60`, User-Agent `shorten-url`, POST form fields `format=json` and `url` only. `shorten(url: str) -> str | None`. Parse JSON; rewrite `http://v.gd/` to `https://v.gd/`; accept only a single-line `https://v.gd/` URL with a nonempty path and no whitespace. At most two attempts. Fatal (HTTP 400 / 406, error codes 1 and 2): log final, return `None`. Rate limit (error code 3 or HTTP 502): print `shorten-url: rate-limited, retrying in 60s` to stderr, flush, `sleep(60)`, second attempt. Transient (timeout, `URLError`, other HTTP 5xx, error code 4, JSON / shape / validation): print `shorten-url: transient error, retrying` to stderr, flush, second attempt immediately. Second-attempt failure: print `shorten-url: <message>` to stderr, flush, return `None`. Do not print the short URL from this module.
5. Generate `shorten-url/scripts/shorten-url/uv.lock` with `uv lock` so it is committed.

### Verify

- `uv run --project shorten-url/scripts/shorten-url shorten-url --help` exits 0 and shows `--url`.
- `uv run --project shorten-url/scripts/shorten-url shorten-url` (no flags) exits `2`.
- `uv run --project shorten-url/scripts/shorten-url shorten-url --url ''` exits `2`.
- `uv run --project shorten-url/scripts/shorten-url shorten-url --url example.com` exits `2`.
- `uv run --project shorten-url/scripts/shorten-url shorten-url --url 'https://example.com' extra` exits `2`.
- `uv run --project shorten-url/scripts/shorten-url shorten-url --url 'https://v.gd/R709K6'` exits `0` and prints exactly `https://v.gd/R709K6` on stdout (pass-through; no network).
- `uv run --project shorten-url/scripts/shorten-url shorten-url --url 'http://v.gd/R709K6'` exits `0` and prints exactly `https://v.gd/R709K6`.
- Read `shorten-url/scripts/shorten-url/src/shorten_url/client.py` and confirm `CREATE_URL`, POST `format=json`, no `shorturl` / `logstats`, timeout `5.0`, wait `60`, the two `shorten-url: ` retry lines, and `User-Agent: shorten-url`.
- Confirm `shorten-url/scripts/shorten-url/pyproject.toml` has empty runtime dependencies and no pytest extra, and that there is no tests tree under `shorten-url/scripts/shorten-url/`.
- Do not pass a non-v.gd long URL to the CLI as part of this stage’s verify.

## Acceptance

- The invoke line `uv run --project <shorten-url-skill-dir>/scripts/shorten-url shorten-url --url U` is a working console script.
- Missing / blank / no-scheme / extra-argv `--url` exits `2` and does not call v.gd.
- An existing `http(s)://v.gd/<code>` URL prints `https://v.gd/<code>` and exits `0` without calling v.gd.
- A create failure after the retry rules exits `4` with a `shorten-url: ` line on stderr and does not print the long URL on stdout.
- No tests were added.
