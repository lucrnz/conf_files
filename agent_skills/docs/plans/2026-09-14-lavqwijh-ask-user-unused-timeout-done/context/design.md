**Archive.** Decisions in this file were current as of 2026-09-14 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# Ask-user unused fuse, shorten-url, and skill dependencies

## Goal

On the SSH path: wait 40 minutes for the first visit to the tunneled wizard, and print a short URL using the same v.gd-then-TinyURL client as the shorten-url skill. Installing a skill that names sibling skills in `DEPENDENCIES.md` also installs those siblings.

## Settled decisions

- **40 minutes, hardcoded.** `DEFAULT_UNUSED_TIMEOUT_SECS = 2400.0`. Not an env var, flag, or per-call override.
- **Unused fuse only.** The timer starts in `HttpPicker.serve_in_thread()` and fires in `_on_unused` if `/opened` has not arrived. After that beacon, still no timeout.
- **Leave the agent tool timeouts alone.** SSH still waits at least 4 hours. Non-SSH / desktop still waits at least 10 minutes.
- **Same unused-fuse exit path.** Unused fire still becomes `NoPicker("not opened")` → exit 4.
- **SKILL.md matches the fuse.** Change only the sentence that says the CLI waits 10 minutes for the tunneled page to be opened. Do not rewrite the adjacent “at least 10 minutes (600000 ms)” desktop tool-timeout sentence.
- **Import `shorten_url.client.shorten`.** Delete `ask_user.shorten`. No subprocess, no second v.gd implementation, no extracted third package.
- **Hard uv path-dep.** `ask-user` depends on the sibling `shorten-url` package via `[tool.uv.sources]`. No lazy import. `uv run` for ask-user fails if the sibling project is missing, desktop included.
- **Raise ask-user to Python 3.11.** `requires-python = ">=3.11,<3.15"`. Do not lower shorten-url.
- **Accept TinyURL GET.** The wizard token may appear on TinyURL’s query string, same as the shorten-url skill.
- **Use shorten-url as-is.** One v.gd attempt (no retry), then TinyURL. User-Agent stays `shorten-url`. On total failure, `shorten()` still returns `None` and ask-user still prints the long Cloudflare URL. `shorten-url: ` failure lines may appear on the same stderr; agents still only relay `ask-user: `.
- **No shortener tests.** Delete `ask-user`’s `test_shorten.py`. Do not add tests to `shorten-url`. Keep ask-user CLI mocks that assert print/exit wiring.
- **Parseable `DEPENDENCIES.md`.** Skill-root sidecar. Empty lines and lines whose first non-space character is `#` are ignored. Every other line is a sibling repo-skill directory name. AGENTS.md does not restate `shorten-url`.
- **Mechanical auto-install.** Installing skill `$name` also installs each listed sibling (recurse, skip already-visited). A listed name that is not a repo skill is an error. No new install CLI; the procedure lives in AGENTS.md and the Agents README one-off follows it.
- **This plan adds `ask-user/DEPENDENCIES.md`** containing `shorten-url`.
- **No ADR.** Timeout constant, client reuse, and an install-procedure note.

## Design

### Unused fuse

`HttpPicker` owns the fuse. `run_ssh_picker` constructs `HttpPicker(payload, token)` with the module default.

```
serve_in_thread()
  start Timer(DEFAULT_UNUSED_TIMEOUT_SECS, _on_unused)
/opened → _mark_opened → cancel timer; wait until submit/cancel
no /opened before the timer → UnusedTimeout → exit 4
```

Change `DEFAULT_UNUSED_TIMEOUT_SECS` from `600.0` to `2400.0`. Tests that inject `unused_timeout_secs=0.05` stay short. The import test that pins the default becomes `2400.0`. `_FakePicker`’s unused constructor default of `600` is not load-bearing; leave it.

### Shorten via shorten-url

`run_ssh_picker` already does `printed = shorten(public) or public`. Point that call at `shorten_url.client.shorten`.

In `ask-user/scripts/ask-user/pyproject.toml`: add a `shorten-url` dependency and a path source to `../../../shorten-url/scripts/shorten-url` (from that pyproject). Relock. Raise `requires-python` to `>=3.11,<3.15`.

Delete `ask_user/shorten.py`. CLI tests that monkeypatch `ask_user.shorten.shorten` patch `shorten_url.client.shorten` instead.

The printed URL may be `https://v.gd/…`, `https://tinyurl.com/…`, or the long `*.trycloudflare.com` URL. README’s SSH paragraph says that. `SKILL.md` still relays whatever follows `ask-user: ` and does not name the shortener.

### Skill dependencies

A skill that needs other repo skills lists them in `DEPENDENCIES.md` at its skill root. Format is defined once in AGENTS.md.

Installing `$name` (OpenCode copy or Agents symlink) also installs each parsed name that is a child of `REPO` containing `SKILL.md`. Recurse through those files. Skip a name already visited in this install. If a line is not a repo skill, stop and report it.

The all-skills Agents loop and “update my opencode skills” already cover every repo skill; they do not need a second copy pass. The one-skill OpenCode path and the Agents README one-off do.

## Stage map

1. **Unused fuse** — Independent of shortening. Smallest production change; SKILL.md wait sentence must move with the constant.
2. **Import shorten-url** — Independent of the fuse. Replaces the bespoke client and creates the hard sibling package dep. Lives in this repo today because both trees exist; a one-skill dest copy would then be broken until stage 03.
3. **DEPENDENCIES.md + install procedure** — Depends on stage 02 creating the reason to list `shorten-url`. Makes one-skill install pull the sibling so the path-dep resolves.

## Out of scope

- Desktop / non-SSH agent tool timeout of 10 minutes
- SSH agent tool timeout of 4 hours
- Making the unused fuse configurable
- Changing behavior after the opened beacon
- Tunnel origin wait, `untun` startup, or shorten-url’s own timeouts / retry policy
- Changing shorten-url’s User-Agent, stderr prefix, or TinyURL GET
- Exit codes or the cannot-open fallback chain
- An ADR
- Tests for v.gd / TinyURL
- A new install CLI or parser program
- `test_cli.py` fake unused-timeout constructor default
- `SKILL.md` naming v.gd or TinyURL

## Assumptions

- 40 minutes is 2400 seconds.
- A user who never opens the URL still gets exit 4 after 40 minutes, then the existing cannot-open fallback.
- Cloudflare / short links from this process remain useful for those 40 minutes; the fuse is the process-side give-up, not a tunnel TTL we control.
- This repo and a first OpenCode dest-prep already contain both skills. The new footgun is a later one-skill copy of ask-user into a dest that lacks shorten-url.
- Anyone who can see the TinyURL create request has the wizard token until Finish or Cancel.
- `shorten_url.client.shorten` stays a `str | None` function with no required CLI passthrough for trycloudflare URLs.
