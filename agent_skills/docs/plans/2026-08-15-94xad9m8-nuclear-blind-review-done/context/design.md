> **Archive.** Decisions in this file were current as of 2026-08-15 (the plan date in the directory name). They may be outdated. Do not treat this as living documentation. This plan directory is an archive.

# Nuclear blind review

## Goal

Add a slash-only isolation skill, `nuclear-blind-review`, that reviews through a temporary stripped tree and a fresh subagent so the verdict is not pair-pressured. Rename `thermo-nuclear-code-quality-review` to `nuclear-review` and split its standards into a code bar and a plan bar that both the in-session skill and the blind skill apply.

## Settled decisions

- New skill name: `nuclear-blind-review`. Slash-only (`disable-model-invocation: true`).
- Rename `thermo-nuclear-code-quality-review` → `nuclear-review`. No trampoline, no old slash alias. Slash-only.
- `nuclear-blind-review` owns only the isolation protocol. Review standards live in `nuclear-review`.
- Park two complete bars beside `nuclear-review/SKILL.md`: `code-bar.md` and `plan-bar.md` (themes, questions, approval). `SKILL.md` keeps scope resolution, per-scope workflow, output envelope, and shared tone.
- Both `/nuclear-review` and `/nuclear-blind-review` classify surfaces and apply the matching bar(s). Blind vs in-session is the only difference.
- Code bar is the current thermo-nuclear standard, moved, not rewritten.
- Plan bar themes: design judo; no leftover multi-option decisions / TBD; stage atomicity and dependency order; checkable acceptance; honest scope and explicit assumptions; feasibility against the current tree; do not launder a bad implementation through the plan. Extra flags when the file is a create-multi-stage-plan stage (`Status` / `Invariants` / `Acceptance` present and usable). Required section: apply `code-bar.md` to the implementation the plan would produce (link, do not copy those rules).
- Plans directory is `docs/plans/` only (repo-root relative). Other folders named `plans/` are ordinary docs.
- Classification is a mechanical path test: any review-surface path under `docs/plans/` → plan job(s); any other review-surface path → code job. Both non-empty → both. The main agent does not skip a surface.
- One plan job per top-level `docs/plans/<dir>/` touched (changes/picker) or per `*-pending` dir (codebase).
- Scopes inherited from today's skill: `changes` (default), `codebase`, `picker`. Picker UX (candidate list, S/E) runs in the real repo; only the reviewer is blinded.
- `scope=codebase`: one code job (omit `docs/plans/`) plus one plan job per `docs/plans/*-pending` directory. Do not audit `*-done` archives.
- When plan jobs > 1: ask parallel vs sequential; if the user declines parallel, run sequential. Code+plan together may run in parallel; the ask is for N plan jobs.
- Threat model: strip parent conversation, git history/blame/commit messages, and any “we decided X” briefing. Ship `AGENTS.md`, README, and other non-plan documentation.
- Code package: stripped source tree without `docs/plans/`; generated unified `DIFF.patch` with `docs/plans/` hunks removed; `FILE_LIST.txt`.
- Plan package: full stripped tree (code included) plus a plan-only `DIFF.patch` (that plan dir’s hunks).
- Stripped tree: no `.git`; honor gitignore; include tracked files and relevant untracked source; skip junk, secrets, DBs, logs, binaries, and files over 5MiB.
- Parent temp dir is created by the Python CLI via `tempfile.mkdtemp` (prefix `nuclear-blind-`), not by a shell `mktemp`. Cleanup is `shutil.rmtree` of that parent. Record the printed path immediately. Delete the parent on every exit (success, spawn fail, copy fail).
- One parent per invocation; per-job child directories under it.
- Copy engine: Python computes the include set, then `shutil.copy2` each relative path. No rsync. No dirsync dependency.
- Each job dir gets the applicable bar file(s) under `_review/` (plan jobs get both bars). Spawn prompt does not include the original repo path.
- Child: `general-purpose`, `capability_mode=read-write`, `cwd` = job dir. Write only `BLIND_REVIEW.md` in that dir. Stay-in-package is honor-system; `spawn_subagent` cannot attach a kernel sandbox.
- Parent reads `BLIND_REVIEW.md` before delete and relays it verbatim. Optional labeled pair-context addendum after the verbatim review. No drop, soften, or re-rank. If the file is missing, fall back to the child’s final message and mark the review degraded.
- Tooling lives under `nuclear-blind-review/scripts/blind-review/` (jp-romaji layout: uv, `pyproject.toml`, pytest). CLI: `jobs`, `prepare`, `cleanup`.
- After rename: re-run the README symlink install and remove the stale `~/.agents/skills/thermo-nuclear-code-quality-review` link.

## Design

`/nuclear-review` stays an in-session review. It gains surface classification and a second bar so a plan-only or mixed change set is not scored with a code-only checklist.

`/nuclear-blind-review` is a wrapper around those same bars. The main agent resolves scope in the real repo (including picker questions), runs `blind-review jobs` to get the mechanical job list, asks parallel-vs-sequential when there are multiple plan jobs, then `prepare`s each job into a shared parent temp directory. Each child sees only its job directory: stripped tree, mechanical diff, file list, and the bar file(s). The main agent never briefs author intent. After every child returns, the parent reads each `BLIND_REVIEW.md`, deletes the parent directory, and prints the reviews as a courier.

The Python CLI is the only place that creates or deletes the temp parent and the only place that decides the include set and diffs. Skill prose must not re-invent rsync flags or `mktemp`.

In-session `/nuclear-review` does not use the CLI or a temp dir. It applies the same classification rules written in `nuclear-review/SKILL.md`. The CLI implements those rules; pytest locks the CLI. Small drift risk is accepted so the non-blind skill does not depend on the blind skill’s package.

## Stage map

Rename first so every later path and slash name is `nuclear-review`. Extract the code bar second so the move is behavior-preserving and `plan-bar.md` can link to a stable file. Then teach `nuclear-review` classification and the plan bar — the in-session skill becomes the source of surface rules the CLI will implement. Then build the uv/pytest CLI against those rules. Last, write `nuclear-blind-review/SKILL.md` so the protocol has a working `jobs` / `prepare` / `cleanup` to call.

## Out of scope

- Kernel / sandbox isolation of the child from the original workspace
- Trampoline or alias for `/thermo-nuclear-code-quality-review`
- Reviewing `docs/plans/*-done` on `scope=codebase`
- Windows as a support bar (macOS/Linux only)
- Auto-invocation of either skill
- Changing `create-multi-stage-plan` or `implement-pending-plans`
- Writing reviews into the real repo

## Assumptions

- Package path is `nuclear-blind-review/scripts/blind-review/`; import package `blind_review`; console script `blind-review`.
- `requires-python >= 3.11`; commit `uv.lock` like jp-romaji.
- `git` is available in the real repo. The CLI fails clearly if it is not.
- Secret/junk patterns (`.env`, `*.pem`, `*.db`, `*.sqlite*`, `*.log`, `node_modules`, `target`, `dist`, `.venv`, `__pycache__`, and similar) are encoded in the CLI and tested, not re-listed in both skills.
- Shared review tone stays in `nuclear-review/SKILL.md` (same tone for both bars unless a later edit says otherwise).
- Sequential plan jobs still share one parent temp dir and still delete it only after the last job.
- Picker dirty-worktree rule is unchanged: warn; do not include uncommitted work.
- Empty job list: stop and say so; do not spawn.
- Home-level Grok rules still load for the child; that leak is accepted.
