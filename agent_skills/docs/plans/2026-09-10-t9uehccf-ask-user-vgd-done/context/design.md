**Archive.** Decisions in this file were current as of 2026-09-10 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# Shorten ask-user tunnel URLs with v.gd

## Goal

On the SSH path, print a phone-copyable wizard URL. After the Cloudflare tunnel origin is known, shorten `{origin}/t/{token}/` with v.gd and put that short URL on the existing `ask-user: ` stderr line. If v.gd cannot shorten, keep the picker working with the long URL.

## Settled decisions

- **v.gd, not is.gd.** Use `https://v.gd/create.php` as specified in [the v.gd shortening API](https://v.gd/apishorteningreference.php). The v.gd preview / continue page before the wizard is accepted.
- **SSH path only.** Desktop Qt never prints a URL. Do not shorten anything else.
- **Random codes.** Do not send `shorturl`. Do not send `logstats`. Do not send `callback`.
- **One stderr line, one URL.** Keep `ask-user: {url}` exactly as today: one flushed line, nothing else on it. On success the `{url}` is the v.gd URL. Never print both the short and the long URL.
- **Agent contract unchanged.** `SKILL.md` still tells the agent to relay whatever follows `ask-user: `. The agent does not need to know it is a shortener.
- **Failure: one immediate retry, then long URL.** Any shorten attempt that does not yield a valid `https://v.gd/…` URL is retried once with no sleep. Second failure → print the original `{origin}/t/{token}/` and continue. Do not exit 4. Do not wait the one minute v.gd suggests after a rate-limit error; blocking the URL line for 60s is worse than falling back.
- **Do not retry a bad long URL.** HTTP 400 / v.gd error code 1, and HTTP 406 / error code 2, fail immediately (no second request).
- **stdlib only.** `urllib.request` POST, `format=json`. No new dependency. No third-party shortener library.
- **5-second timeout** per attempt (`SHORTEN_TIMEOUT_SECS = 5.0`).
- **POST, not GET.** Same parameter names as the API GET examples, in an `application/x-www-form-urlencoded` body, so the secret path token is not on the v.gd request line.
- **No stats, no custom alias, no cache.** Each tunnel URL is unique; do not persist mappings.
- **Tests stay offline.** Mock the HTTP call. Never hit v.gd, never spawn `untun`, never construct `QApplication`.
- **No ADR.** This does not need a living project doc.

## Design

`run_ssh_picker` already builds `public = {origin}/t/{token}/` and prints it. Insert one call after `public` is known and before the stderr print:

```
public = f"{tunnel.origin.rstrip('/')}/t/{token}/"
printed = shorten(public) or public
print(f"ask-user: {printed}", file=sys.stderr, flush=True)
```

`shorten` lives in a new Qt-free module `ask_user/shorten.py`. It does not know about tunnels or the CLI. It returns `str | None`.

```
POST https://v.gd/create.php
  format=json
  url=<public, form-encoded>
  User-Agent: ask-user
  timeout=5s
```

Success: HTTP 200 and JSON `{"shorturl": "https://v.gd/R709K6"}`. Accept that value if it is a single-line `https://v.gd/` URL with a non-empty path and no whitespace. If the API returns `http://v.gd/…`, rewrite the scheme to `https` and then apply the same checks. Anything else is a failed attempt.

Retry (immediately, once) on: timeout, `URLError`, HTTP 5xx (including 502/503), v.gd error codes 3 and 4, JSON / shape / validation failure.

No retry on: HTTP 400, HTTP 406, v.gd error codes 1 and 2.

`run_ssh_picker` lazy-imports `shorten` the same way it imports `http_wizard` and `tunnel`. Existing teardown, unused fuse, and exit table do not change. The unused fuse still starts at `serve_in_thread()`, after the URL line is printed.

## Stage map

1. **v.gd client** — The POST, parse, validate, and retry rules are independent of the CLI. Tests can pin them with a fake `urlopen` before any print contract moves.
2. **Wire SSH print** — Depends on `shorten()` existing. This is the only stage that changes what the user is told to open. CLI tests must mock `shorten` so CI cannot call v.gd.
3. **README** — After the print contract is real, say that the relayed URL is usually a v.gd link (preview page is normal) and that a long Cloudflare URL means shortening failed. `SKILL.md` is left alone so the agent relay rule stays a single fact.

## Out of scope

- is.gd or any other shortener
- Custom `shorturl` aliases
- `logstats`
- Deleting or expiring short links
- Changing the path token, unused fuse, or exit table
- New Python or Node dependencies
- Live v.gd or live `untun` in pytest
- `SKILL.md` edits
- An ADR
- Repo-root `README.md` or `AGENTS.md` edits

## Assumptions

- Outbound HTTPS from the SSH host to `v.gd` is usually available on the same machines that can already reach npm and Cloudflare for `untun`. If it is not, fallback to the long URL is correct.
- v.gd short links are permanent. A token URL remains reachable only while this process’s tunnel is up; after teardown the short link 404s at the origin. That is acceptable.
- Anyone who has the short URL can open the wizard until Finish or Cancel, same as anyone who had the long URL.
- Chat unfurls of `v.gd` hit v.gd’s preview page, not the wizard GET, so they still must not count as opened (the opened beacon stays a POST from the page JS).
- Skill-design-principles apply: one home per fact; first-run / human notes in `README.md` only.
