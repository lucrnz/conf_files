# Stage 05: nuclear-blind-review skill protocol

## Status
done

## Description

Write `nuclear-blind-review/SKILL.md`: the isolation protocol that calls the stage 04 CLI, spawns stay-in-package subagents, relays `BLIND_REVIEW.md` verbatim, and always deletes the parent temp dir.

## Rationale

The CLI is unusable as a skill until an agent is told the exact order: resolve scope, `jobs`, maybe ask parallel, `prepare`, spawn, read, `cleanup` on every path. This stage is that contract.

## Invariants

- Slash-only (`disable-model-invocation: true`).
- No copy/exclude/mktemp logic in prose; those are CLI invocations only.
- Original repo path never appears in the spawn prompt.
- Parent temp dir is deleted on success, spawn failure, and prepare failure.
- Courier: verbatim `BLIND_REVIEW.md` per job; optional labeled pair-context addendum after; no drop/soften/re-rank.
- Review standards are not restated; children are told to apply the `_review/` bar files.

## Risks

- An agent that “helpfully” summarizes the child defeats the skill. The courier rule must be a hard step, not a tone note.
- Forgetting `cleanup` leaks trees and any secrets that slipped the filter. Cleanup is a required step in every exit path, including errors.

## Implementation

### Files

- `nuclear-blind-review/SKILL.md` (create)
- Re-run README symlink install so `~/.agents/skills/nuclear-blind-review` exists

### Steps

1. Frontmatter: `name: nuclear-blind-review`; description states blind/isolated nuclear review, pair-pressure-free subagent, `/nuclear-blind-review`; `disable-model-invocation: true`.
2. Body, in execution order:
   1. Resolve `scope` exactly as `nuclear-review` (`changes` default, `codebase`, `picker` with the same S/E questions). Picker and git commands run in the real repo.
   2. Resolve this skill’s directory (follow the symlink). Invoke:
      `uv run --project <skill>/scripts/blind-review blind-review`
   3. `jobs` with `--repo` and `--surface` (and `--range` for picker). Empty list → report and stop.
   4. If plan jobs > 1: ask parallel vs sequential (questions tool if available); recommended = parallel; decline → sequential.
   5. `prepare` each job. First prepare may omit `--parent`; later prepares pass the printed parent. Pass `--bar` paths to `nuclear-review/code-bar.md` and, for plan jobs, also `plan-bar.md` (resolve `nuclear-review` the same way jp-romaji resolves its skill dir). Record `parent` immediately.
   6. Spawn one subagent per job: `subagent_type=general-purpose`, `capability_mode=read-write`, `cwd=<job_dir>`, `isolation` omitted (not worktree). Prompt may include: package kind, scope label, that git history is absent by design, paths *relative to cwd* (`DIFF.patch`, `FILE_LIST.txt`, `_review/`, write `BLIND_REVIEW.md`). Prompt must not include the original repo path, user justifications, “we decided”, author names, or “be fair”. Instruct: read only this job dir; write only `BLIND_REVIEW.md`.
   7. Parallel = spawn all then wait; sequential = one spawn at a time. Same parent.
   8. For each job: read `BLIND_REVIEW.md`. If missing, use the child’s final message and label the section degraded.
   9. `blind-review cleanup --parent PARENT`. If a spawn or prepare failed, still cleanup before talking to the user about the failure.
   10. Output: state scope, job list, that the temp parent was deleted. Print each review verbatim under a heading (`code` / `plan <dir>`). Then an optional `Pair context` addendum from the main agent. Do not drop, soften, or re-rank findings.
3. Do not embed code-bar or plan-bar text in this file.
4. Symlink-install the new skill.

### Verify

- `test -f nuclear-blind-review/SKILL.md`
- Frontmatter name is `nuclear-blind-review` and `disable-model-invocation` is true
- `SKILL.md` contains the `cleanup` invocation and an explicit “every exit path” requirement
- `SKILL.md` forbids putting the original repo path in the spawn prompt
- `SKILL.md` does not restate Rule/Flag/Remedy themes
- `ls -la ~/.agents/skills/nuclear-blind-review` points at this repo’s directory
- Dry-read the protocol against [design.md](context/design.md): every settled isolation decision appears as a step or a prohibition

## Acceptance

- `/nuclear-blind-review` is installable and slash-only.
- Following the skill cannot skip cleanup, cannot brief pair intent, and cannot apply a bar other than the files in `_review/`.
- Mixed surfaces produce one child per `jobs` line, not a single merged child.
- The main agent’s only allowed extra text is a labeled pair-context addendum after the verbatim reviews.
