---
name: shorten-url
description: Shorten a URL with v.gd. Use when the user wants to shorten a URL or runs /shorten-url.
---

# shorten-url

Shorten only URLs the user asked to shorten. Do not scrape every link in the message.

If a target has no scheme and is clearly a web URL, prepend `https://` before invoking.

One CLI call at a time, never in parallel. Several URLs are a sequential loop.

Chat output is `original → short`. Several URLs become a list.

## Mechanical CLI

This skill lives in the directory that contains this `SKILL.md`. Follow the symlink if you reached it via `~/.agents/skills/shorten-url`. Resolve that directory, then:

```
uv run --project <that-dir>/scripts/shorten-url shorten-url --url <url>
```

Never invoke with a cwd-relative `shorten-url/scripts/shorten-url` path. Set the command timeout to at least 3 minutes (180000 ms if the tool uses milliseconds).

As soon as stderr contains a line starting with `shorten-url: `, print the rest of that line to the user immediately and keep waiting.

On exit 0, the single stdout line is the short URL. Show `original → short`.

On exit 2, if the only problem is a missing scheme, prepend `https://` and run once more. Otherwise report stderr and skip that URL.

On exit 4 or any other non-zero: mention the failure once, do not re-run the CLI for that URL, and continue any remaining URLs.
