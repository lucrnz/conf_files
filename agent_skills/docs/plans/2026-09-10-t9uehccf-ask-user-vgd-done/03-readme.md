# Stage 03: README

## Status
done

## Description

Tell a human reading `ask-user/README.md` that the relayed SSH URL is usually a v.gd short link (a preview page before the wizard is normal) and that a long `*.trycloudflare.com` URL means shortening failed and they should still open it.

## Rationale

Stage 02 changes what appears in chat. The agent relay rule in `SKILL.md` does not need to know about v.gd; the human who is copying the URL on a phone does.

## Invariants

- Do not edit `ask-user/SKILL.md`. The relay rule stays “print the rest of the `ask-user: ` line”.
- Do not edit repo-root `README.md` or `AGENTS.md`.
- Do not document is.gd, custom aliases, API parameters, or a second invoke line.
- First-run `pnpx` / `untun` / `cloudflared` notes stay in this README only.

## Risks

If the README still says only “HTTPS URL”, a v.gd preview page will look like a failure. Name v.gd and the preview page in the SSH section.

## Implementation

### Files

- `ask-user/README.md`

### Steps

1. In the SSH section of `ask-user/README.md`, keep “the agent prints an `ask-user: ` HTTPS URL; open that URL; do not open `127.0.0.1`”. Add that the printed URL is normally a `https://v.gd/…` short link to the tunneled wizard, that v.gd may show a preview / continue page first, and that a long `*.trycloudflare.com` URL means shortening failed and should still be opened. Do not add flags, API usage, or an `ssh -L` recipe.

### Verify

- Read `ask-user/README.md` and confirm the SSH section names `v.gd`, the preview page, fallback to `trycloudflare.com`, and the existing “do not open `127.0.0.1`” rule.
- `rg "v.gd" ask-user/SKILL.md` is empty.
- The local smoke `printf` command in that README is unchanged.

## Acceptance

- A human who only reads `ask-user/README.md` expects a short v.gd link, will click through a preview page, and will still open a long Cloudflare URL if that is what was printed.
- An agent that only reads `ask-user/SKILL.md` still relays the `ask-user: ` line and does not learn a second URL format.
