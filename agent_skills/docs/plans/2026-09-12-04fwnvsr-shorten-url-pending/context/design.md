# Shorten-url skill

## Goal

Add a `shorten-url` skill the agent auto-invokes when the user wants to shorten a URL, backed by a companion `uv` CLI that POSTs to [v.gd’s shortening API](https://v.gd/apishorteningreference.php) and prints one `https://v.gd/…` URL.

## Settled decisions

- **Name.** Skill directory, frontmatter `name`, console script, and slash command are `shorten-url`.
- **Auto-invoke.** No `disable-model-invocation`. Description is exactly: `Shorten a URL with v.gd. Use when the user wants to shorten a URL or runs /shorten-url.`
- **Independent CLI.** New `uv` project at `shorten-url/scripts/shorten-url`. Do not import `ask-user`. Skills are per-directory symlinks; coupling would break a lone install. Wire shape matches the existing v.gd client (POST, `format=json`, 5s timeout, stdlib `urllib`) but the exit and log contract is different.
- **One URL per process.** Required `--url`. Extra argv is usage failure. Agent loops if the user asked to shorten several URLs.
- **Random codes only.** Do not send `shorturl`, `logstats`, or `callback`.
- **Stdout.** Success prints one `https://v.gd/…` line and nothing else. The agent, not the CLI, shows `original → short` in chat.
- **Fail loud.** v.gd / network failure is a non-zero exit and a stderr message. Never print the long URL as if it were short.
- **Already v.gd.** Host `v.gd` (case-insensitive) with a nonempty path code is pass-through: print `https://v.gd/` plus that path (and query/fragment if present), exit 0, no API call. `http://` is rewritten to `https://`. Do not special-case is.gd. `https://v.gd/` with an empty path is not pass-through.
- **Scheme required.** After strip, `--url` must start with `http://` or `https://` (scheme case-insensitive). Missing scheme or embedded whitespace is usage failure (exit 2). The agent may prepend `https://` if the user clearly meant a web URL, then re-run.
- **Targets.** The agent shortens only URLs the user asked to shorten. It does not scrape every link in the message.
- **Batch.** One CLI call at a time, never in parallel. If one URL fails, report it and continue the rest. Do not re-run the CLI for a URL that already failed.
- **Retries.** At most two attempts. Fatal (HTTP 400 / 406, v.gd error codes 1 and 2): no retry. Transient (timeout, `URLError`, HTTP 5xx other than 502, v.gd error code 4, JSON / shape / validation failure): one immediate retry. Rate limit (v.gd error code 3 or HTTP 502): log, `sleep` 60 seconds, then one retry. If the second attempt fails for any reason, stop (do not sleep after the last attempt).
- **Stderr logs.** Every diagnostic is one flushed line starting with `shorten-url: `. Immediate retry: `shorten-url: transient error, retrying`. Rate-limit wait: `shorten-url: rate-limited, retrying in 60s`. Final failure: `shorten-url: <v.gd errormessage, or a short class such as timeout>`. Success and pass-through print nothing on stderr. Usage (exit 2) may use argparse’s normal usage text.
- **Agent timeout.** The invoke command’s timeout is at least 3 minutes (180000 ms) so a 60s wait plus two 5s attempts and `uv` startup can finish. As soon as stderr contains a line starting with `shorten-url: `, the agent prints the rest of that line to the user and keeps waiting.
- **No tests.** No `tests/` directory, no pytest extra, no live v.gd in verify.
- **No README.** No `shorten-url/README.md`. Failure text lives in `SKILL.md` (mention stderr, do not retry that URL). No pointer at a missing README.
- **No slash alias.** `/shorten-url` is enough. No `disable-model-invocation` sibling skill.
- **No cache.** Do not persist long→short mappings.
- **No ADR.** This is a new isolated skill, not a repo-wide decision other skills must cite.
- **No install step.** After the files exist, the repo-root `README.md` symlink loop already picks up any `*/SKILL.md` directory. Do not edit that README or `AGENTS.md`.

## Design

`shorten-url/SKILL.md` is the agent contract. `shorten-url/scripts/shorten-url` is the only process that talks to v.gd.

**Invoke.** Resolve the directory that contains this `SKILL.md` (follow a symlink if reached via `~/.agents/skills/shorten-url`). Then:

```
uv run --project <that-dir>/scripts/shorten-url shorten-url --url <url>
```

Never invoke with a cwd-relative `shorten-url/scripts/shorten-url` path. `--url` is required; strip it; empty is usage failure.

**CLI layout.** Python 3.11+, no runtime dependencies, `uv_build`, module `shorten_url` under `src`, console script `shorten-url = "shorten_url.cli:main"`.

- `shorten_url.cli` — argparse, validation, pass-through, exit codes. Prints the short URL on stdout only on success.
- `shorten_url.client` — POST / parse / retry / stderr logs. Returns `str | None`. Does not print the short URL.

**Validation (exit 2, no API).** Missing `--url`; extra positional argv; blank after strip; any whitespace remaining after strip; scheme is not `http` or `https`.

**Pass-through (exit 0, no API).** Parse the URL. Host equals `v.gd` case-insensitively, scheme is `http` or `https`, and the path has a nonempty code (not `""` or `"/"`). Print `https://v.gd/` + original path (without a leading-slash double-up) + query + fragment. Do not call v.gd.

**Create.**

```
POST https://v.gd/create.php
  format=json
  url=<long URL, form-encoded>
  User-Agent: shorten-url
  timeout=5s
```

Success: HTTP 200 and JSON `{"shorturl":"https://v.gd/R709K6"}`. Rewrite a leading `http://v.gd/` to `https://v.gd/`. Accept only a single-line `https://v.gd/` URL with a nonempty path and no whitespace. Anything else is a failed attempt.

Retry classification:

| First attempt | Next |
|---|---|
| valid short URL | print it, exit 0 |
| HTTP 400 / 406, or JSON `errorcode` 1 or 2 | log final, exit 4 |
| JSON `errorcode` 3, or HTTP 502 | log wait, sleep 60s, second attempt |
| timeout, `URLError`, other HTTP 5xx, `errorcode` 4, bad JSON / shape / validation | log retry, second attempt immediately |
| second attempt anything but a valid short URL | log final, exit 4 |

Final message prefers v.gd’s `errormessage` when present; otherwise a short class (`timeout`, `network error`, `HTTP {code}`, `invalid response`, `rate limited`).

**Exit codes.**

| Code | Meaning |
|---|---|
| 0 | printed one `https://v.gd/…` line (created or pass-through) |
| 2 | usage / invalid `--url` |
| 4 | could not shorten after the retry rules |

**Skill body.** When to fire; only requested URLs; one-at-a-time loop; `original → short` in chat; the uv invoke line; 3-minute timeout; relay `shorten-url: ` lines immediately; continue after a per-URL failure; do not retry a URL the CLI already failed; on exit 2 the agent may fix a missing scheme and re-run once; on exit 4 mention the stderr and move on. No first-run essay (there is none). No README pointer.

## Stage map

1. **CLI** — The skill has nothing to run until the uv project, flags, pass-through, POST, retry/sleep, logs, and exit codes exist. Verify can exercise usage and pass-through without touching v.gd.
2. **Skill** — `SKILL.md` describes that CLI. It ships second so the invoke line, timeout, and stderr prefix are real.

## Out of scope

- is.gd or any other shortener
- Custom `shorturl` aliases and `logstats`
- Persistent cache
- Batching many URLs in one CLI process
- Tests, pytest, a `--dry-run` flag
- `README.md` for this skill
- A slash-only alias skill
- An ADR
- Repo-root `README.md` or `AGENTS.md` edits
- Installing or updating `~/.agents/skills` or OpenCode copies
- Extracting a shared v.gd library with `ask-user`
- Live v.gd calls in verify

## Assumptions

- `uv` is on the machine that implements and on machines that use the skill.
- Outbound HTTPS from the agent host to `v.gd` is usually available. If it is not, exit 4 is correct.
- v.gd short links are permanent. That is acceptable.
- v.gd’s per-IP limit is 200 shortens per hour (100 with stats). Sequential one-URL calls stay inside that for interactive use.
- After the files exist, install is the existing per-skill symlink loop in the repo `README.md`.
- Skill-design-principles apply: one home per fact; thin `SKILL.md`; no duplicated API essay.
