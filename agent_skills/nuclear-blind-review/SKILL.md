---
name: nuclear-blind-review
description: Isolated nuclear review via a temp stripped tree and a fresh subagent (no pair-pressure). Triggers: nuclear-blind review, blind nuclear review, isolated nuclear review. Use when the user runs /nuclear-blind-review. Same scopes as nuclear-review (changes / codebase / picker).
disable-model-invocation: true
---

# Nuclear Blind Review

Isolation wrapper around `nuclear-review`. Do not restate the bars. Do not invent copy flags or temp paths.

## CLI

This skill lives in the directory that contains this `SKILL.md`. Follow the symlink if you reached it via `~/.agents/skills/nuclear-blind-review`. Resolve that directory as `<skill>`, then:

```
uv run --project <skill>/scripts/blind-review blind-review
```

Resolve `nuclear-review` the same way (follow its symlink). Bars: `<nuclear-review>/code-bar.md`, `<nuclear-review>/plan-bar.md`.

## Protocol

1. Resolve `scope` exactly as `nuclear-review` (`changes` default, `codebase`, `picker` with the same S/E questions). Picker and all git commands run in the real repo.
2. `jobs --repo <real-repo> --surface <scope>` (`--range` for picker). Empty `jobs` → report and **stop**. Do not spawn.
3. If plan jobs > 1: ask parallel vs sequential (questions tool if available). Recommended = parallel. Decline → sequential.
4. `prepare` each job. First call may omit `--parent`; later calls pass the printed `parent`. Always pass `--bar <nuclear-review>/code-bar.md`. For `kind=plan` also pass `--bar <nuclear-review>/plan-bar.md`. Record `parent` immediately.
5. Spawn **one subagent per `jobs` line** (`subagent_type=general-purpose`, `capability_mode=read-write`, `cwd=<job_dir>`, do not set `isolation=worktree`).
   - Prompt may include: package kind, scope label, that git history is absent by design, paths **relative to cwd** (`DIFF.patch`, `FILE_LIST.txt`, `_review/`), and “write `BLIND_REVIEW.md` applying the bar file(s) in `_review/`”.
   - Prompt must **not** include the original repo path, user justifications, “we decided”, author names, or “be fair”.
   - Instruct: read only this job dir; write only `BLIND_REVIEW.md`.
6. Parallel = spawn all then wait. Sequential = one spawn at a time. Same parent.
7. For each job: read `BLIND_REVIEW.md`. If missing, use the child’s final message and label that section **degraded**.
8. `cleanup --parent <parent>` on **every exit path** — success, spawn failure, prepare failure — **before** explaining a failure to the user.
9. Output: state scope, the job list, and that the temp parent was deleted. Print each review **verbatim** under `code` or `plan <dir>`. Then an optional `Pair context` addendum. Do not drop, soften, or re-rank findings.

Stay-in-package is honor-system (`spawn_subagent` cannot sandbox the original repo). Cleanup is not optional.
