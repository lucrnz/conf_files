# Stage 04: blind-review CLI (jobs, prepare, cleanup)

## Status
done

## Description

Create the uv/pytest Python package that owns temp-parent creation, job classification, stripped-tree copy, mechanical diffs, and deletion. No `SKILL.md` in this stage beyond what is needed for the package to live under `nuclear-blind-review/scripts/blind-review/`.

## Rationale

The blind skill must not improvise `mktemp` or copy flags. The CLI is the single implementation of the stage 03 path tests plus the isolation package shape. Tests lock that before prose tells an agent to call it.

## Invariants

- Parent directory is created only by `tempfile.mkdtemp(prefix="nuclear-blind-")`.
- Cleanup is `shutil.rmtree` of that parent. Refuse to delete a path whose basename does not start with `nuclear-blind-`.
- Include set is computed in Python (`git ls-files`, allowed untracked, filters). Copy is `shutil.copy2` of those relative paths. No rsync, no dirsync dependency.
- Code jobs omit `docs/plans/` from the tree and from `DIFF.patch`.
- Plan jobs include the full stripped tree and a plan-only diff for that `--plan-dir`.
- `scope=codebase` plan jobs are `*-pending` dirs only.
- macOS/Linux only; fail clearly if `git` is missing.

## Risks

- Tests that shell out to a real `git` repo fixture are the only proof the include set matches the skill rules. Fixture repos must cover mixed surfaces, gitignored junk, a secret-like file, a `*-done` plan, and a file over 5MiB.
- `cleanup` on a wrong path is catastrophic; the prefix check is mandatory.

## Implementation

### Files

- `nuclear-blind-review/scripts/blind-review/pyproject.toml`
- `nuclear-blind-review/scripts/blind-review/uv.lock`
- `nuclear-blind-review/scripts/blind-review/src/blind_review/__init__.py`
- `nuclear-blind-review/scripts/blind-review/src/blind_review/cli.py`
- other `src/blind_review/*.py` as needed (jobs, prepare, cleanup, copy, diff)
- `nuclear-blind-review/scripts/blind-review/tests/test_jobs.py`
- `nuclear-blind-review/scripts/blind-review/tests/test_prepare.py`
- `nuclear-blind-review/scripts/blind-review/tests/test_cleanup.py`
- fixture helpers under `tests/` as needed

### Steps

1. Scaffold like `jp-romaji/scripts/romaji/`: `requires-python >= 3.11`, hatch/uv build, `[project.scripts] blind-review = "blind_review.cli:main"`, pytest in the dev group. Runtime deps: none beyond stdlib (no rsync, no dirsync).
2. Implement:
   - `blind-review jobs --repo ROOT --surface changes|codebase|picker [--range GIT_RANGE]`
     Prints JSON: a list of jobs `{id, kind: code|plan, plan_dir?}`. Empty list is valid. Classification matches [03](03-plan-bar-and-surfaces.md) / [design.md](context/design.md).
   - `blind-review prepare --repo ROOT --surface … [--range] --kind code|plan [--plan-dir DIR] [--parent PARENT] [--bar PATH]…`
     If `--parent` is omitted, `mkdtemp(prefix="nuclear-blind-")` and use that parent. Create `PARENT/<job-id>/`. Copy the include set with `shutil.copy2`. Write `DIFF.patch` and `FILE_LIST.txt`. Copy each `--bar` into `<job-id>/_review/`. Print JSON `{parent, job_dir, job}`.
   - `blind-review cleanup --parent PARENT`
     Delete `PARENT` only if its basename starts with `nuclear-blind-` and it is a directory. Exit non-zero otherwise.
3. Include-set filters: honor gitignore (do not copy ignored files); drop `.git`; drop secrets/junk/DB/log/binary patterns listed in [design.md](context/design.md) assumptions; drop files `> 5MiB`; for `--kind code`, drop `docs/plans/**`; for codebase `--kind plan`, only that `--plan-dir`’s plan files in the *diff*, but the tree is the full stripped tree (including that pending plan dir, excluding `*-done` siblings if easy; at least do not require `*-done` in the plan-only DIFF).
4. `changes` surface: staged ∪ unstaged ∪ relevant untracked, like today’s nuclear-review. `picker`: `--range` is a git revision range the caller already resolved (e.g. `S^..E`). `codebase`: no range; whole tree as include set.
5. Tests with temporary git repos:
   - mixed repo → `jobs` emits one code job and one plan job per touched `docs/plans/<dir>/`
   - codebase → no `*-done` plan jobs; one job per `*-pending`
   - gitignored `node_modules` / `*.log` / `.env` not copied
   - tracked file `> 5MiB` not copied
   - code `DIFF.patch` has no `docs/plans/` hunks
   - plan `DIFF.patch` has only that plan dir
   - `prepare` without `--parent` creates a `nuclear-blind-` prefix dir
   - `cleanup` removes it; `cleanup` of `/tmp/not-ours` fails and leaves it
6. Document the invoke line in a one-paragraph `scripts/blind-review/README.md` (uv run --project …) so stage 05 can quote it. Do not write the agent skill yet.

### Verify

```
uv run --project nuclear-blind-review/scripts/blind-review pytest
```

Must pass. Also run a smoke `jobs` / `prepare` / `cleanup` against this agent_skills repo and confirm the parent dir is gone afterward.

## Acceptance

- `uv run --project nuclear-blind-review/scripts/blind-review pytest` is green.
- `pyproject.toml` has no `dirsync` or rsync wrapper dependency.
- A prepare+cleanup smoke run leaves no `nuclear-blind-*` directory behind.
- `jobs` output on a fixture with code + two plan dirs is three jobs (1 code + 2 plan), not one combined plan job.
