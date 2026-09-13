# Stage 02: Skill

## Status
pending

## Description

Write the auto-invoke `shorten-url` skill that tells the agent when to fire, how to run the CLI from stage 01, what to print in chat, and how to handle stderr and failures.

## Rationale

The CLI is unusable as a skill until a description matches “shorten a URL” / `/shorten-url` and a thin body states the invoke line, timeout, and relay rules. There is no README; those rules have to live in `SKILL.md`.

## Invariants

- `shorten-url/SKILL.md` does not set `disable-model-invocation`.
- The `description` field is exactly the settled string in [context/design.md](context/design.md).
- No `shorten-url/README.md`. The skill must not point at a README.
- The skill does not restate the v.gd POST body, retry matrix, or exit-code table (those stay in the CLI / this plan). It states when to run, the invoke line, the timeout, stderr relay, chat mapping, and per-URL failure behaviour.

## Risks

A vague description will miss “shorten this URL” or will fire on unrelated “shorten” talk (git, text). The description must say it shortens a URL with v.gd and list `/shorten-url`. The body must say only URLs the user asked to shorten.

## Implementation

### Files

- `shorten-url/SKILL.md`

### Steps

1. Write `shorten-url/SKILL.md` with frontmatter `name: shorten-url` and `description` exactly: `Shorten a URL with v.gd. Use when the user wants to shorten a URL or runs /shorten-url.` Do not set `disable-model-invocation`.
2. In the skill body, state: fire when this request asks to shorten a URL or runs `/shorten-url`; shorten only URLs the user asked to shorten; if a scheme is missing and the user clearly meant a web URL, prepend `https://` and then invoke; one CLI call at a time, never in parallel; several URLs are a sequential loop; chat output is `original → short` (a list if several).
3. Add a Mechanical CLI section: this skill lives in the directory that contains this `SKILL.md`; follow the symlink if reached via `~/.agents/skills/shorten-url`; resolve that directory, then `uv run --project <that-dir>/scripts/shorten-url shorten-url --url <url>`. Never a cwd-relative `shorten-url/scripts/shorten-url` path. Set the command timeout to at least 3 minutes (180000 ms if the tool uses milliseconds).
4. State: as soon as stderr contains a line starting with `shorten-url: `, print the rest of that line to the user immediately and keep waiting. On exit 0, read the single stdout line as the short URL and show `original → short`. On exit 2, if the only problem is a missing scheme, prepend `https://` and run once more; otherwise report stderr and skip that URL. On exit 4 or any other non-zero, mention the failure once, do not re-run the CLI for that URL, and continue any remaining URLs. Do not point at a README.

### Verify

- Read `shorten-url/SKILL.md`. Confirm frontmatter name `shorten-url`, no `disable-model-invocation`, and the description is exactly the settled string.
- Confirm the body has: only requested URLs, sequential loop, `original → short`, the uv invoke line, 3-minute / 180000 ms timeout, `shorten-url: ` stderr relay, continue-after-failure, no retry of a failed URL, and a one-shot missing-scheme fix.
- Confirm `shorten-url/SKILL.md` does not mention `README.md`, does not list v.gd form fields, and does not enumerate HTTP status codes.
- Confirm there is no `shorten-url/README.md`.

## Acceptance

- An agent that only reads `shorten-url/SKILL.md` knows when to fire, which URLs to pass, how to invoke the CLI, how long to wait, what to show in chat, and what to do on stderr / exit 2 / exit 4.
- The skill body does not duplicate the CLI’s POST/retry implementation and does not point at a README.
