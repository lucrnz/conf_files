# Stage 04: Skill and README

## Status
done

## Description

Update `ask-user/SKILL.md` and `ask-user/README.md` for the SSH path: auto-switch, `ask-user: ` relay, 4-hour SSH block, exit 4 meanings, and first-run `pnpx`/`untun` notes. Point at the existing CLI; do not invent flags. Optionally retitle the uv project description to mention the SSH picker.

## Rationale

Stages 01–03 are invisible to an agent that still reads the v1 skill (10-minute block, “desktop window”, no URL relay). The skill is the only place those mechanical duties can live. First-run tunnel download does not belong in the skill body.

## Invariants

- `ask-user/SKILL.md` does not set `disable-model-invocation`.
- Prefer native questions tool; do not dual-fire. That sentence stays.
- First-run PySide6, display, pnpx, `cloudflared` download, and Cloudflare notice appear only in `ask-user/README.md`. The skill may point at that file.
- Do not patch other skills. Do not edit the repo-root `README.md` or `AGENTS.md`.
- Do not document `ssh -L`, LAN bind, or a second invoke line.

## Risks

If the description still says only “desktop window”, SSH-only agents may skip the skill. The description must mention the tunneled page without dropping the missing-questions-tool trigger.

If the skill forgets the 4-hour SSH block, the harness will kill a picker the user has already opened (the CLI fuse is off after the beacon).

## Implementation

### Files

- `ask-user/SKILL.md`
- `ask-user/README.md`
- `ask-user/scripts/ask-user/pyproject.toml`

### Steps

1. Edit `ask-user/SKILL.md` frontmatter `description` to: `Present multiple-choice questions (N options + Other) when no questions tool is available. Uses a desktop window locally, or a tunneled browser page over SSH. Use when you need the user to choose among options and \`ask_user_question\` / a questions tool is not available. Use when the user runs \`/ask-user\`.` Keep `name: ask-user`. Do not set `disable-model-invocation`.
2. In the skill body, keep fallback-only, self-contained questions, no agent-supplied Other, recommended-first, the same uv invoke line, and stdin/stdout JSON shapes. Replace the single “≥10 minutes, CLI has no timeout” rule with: if the command environment has a non-empty `SSH_CONNECTION`, `SSH_CLIENT`, or `SSH_TTY`, set the tool timeout to at least 4 hours (`14400000` ms); otherwise at least 10 minutes (`600000` ms). The CLI unused-fuse is 10 minutes until the page beacons; after that the CLI does not time out.
3. In that same file, add the SSH mechanical duties from [context/design.md](context/design.md): the CLI auto-detects SSH and will not open Qt; as soon as stderr has a line starting with `ask-user: `, print the rest of the line to the user immediately and keep waiting; that line is the wizard URL, not the answers JSON. Do not tell the agent to pass flags or to detect SSH for the purpose of choosing a binary.
4. In that same file, keep the exit table 0 / 2 / 4 / 6. Clarify that 4 means the picker could not be presented (no display, no tunnel, or the URL was never opened). Exit 4 or 6 → numbered options in chat, do not retry. Exit 2 → report stderr, do not retry. Keep the `README.md` pointer. Do not copy first-run install steps into the skill.
5. Edit `ask-user/README.md`: keep the PySide6 / display smoke path. Add a first-run SSH note only here: `pnpx` (else `npx`) will download `untun` and `cloudflared`; Cloudflare’s notice is accepted via the CLI env; the agent (not the human) prints the `ask-user: ` URL; the human opens that URL, not `127.0.0.1`. Do not invent flags. Do not add an `ssh -L` recipe.
6. In `ask-user/scripts/ask-user/pyproject.toml` change `description` to `Ask multiple-choice questions in a desktop window or a tunneled page.` Do not add Node or extra Python dependencies.

### Verify

- Read `ask-user/SKILL.md`. Confirm the new description contains `tunneled` and `SSH` and still contains `ask_user_question`, `questions tool is not available`, and `/ask-user`; no `disable-model-invocation`; fallback-only; the uv invoke line; `14400000` and `600000`; the `ask-user: ` relay; exits 0/2/4/6; fallback on 4 and 6; a README pointer.
- Grep `ask-user/SKILL.md` for `cloudflared`, `pnpx`, `unpkg`, `ssh -L`, and smoke-test `printf` — those must not appear as setup steps in the skill (a `README.md` pointer is fine).
- Read `ask-user/README.md`. Confirm the local smoke command still uses `uv run --project scripts/ask-user ask-user`, and that SSH first-run mentions `pnpx`/`npx` and forbids treating localhost as the user URL.
- Read `ask-user/scripts/ask-user/pyproject.toml` and confirm the description change and that `dependencies` is still only `PySide6`.

## Acceptance

- An agent that only reads `ask-user/SKILL.md` knows when to fire, how to invoke, how long to block on SSH vs local, to relay the `ask-user: ` URL, and to fall back in chat on exit 4 or 6.
- A human who only reads `ask-user/README.md` knows the first `untun` run will download tools and that they open the relayed HTTPS URL.
- No other skill and no repo-root install doc was edited.
