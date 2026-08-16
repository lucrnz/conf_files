# Stage 01: plan-id mint CLI

## Status
done

## Description

Add a uv/pytest package under `create-multi-stage-plan/scripts/plan-id/` that mints a collision-checked plan directory basename. Collision is “this exact basename is already an immediate child.” No skill prose in this stage except a one-paragraph package README so stage 03 can quote the invoke line.

## Rationale

Agents must not invent ids or increment a shared counter. Slug/date checks, the draw, and basename retry belong in one tested program before the create skill calls it.

## Invariants

- Console script `plan-id`; only subcommand is `mint`.
- Modules are `cli.py` (argparse) and `names.py` (validate, draw, basename retry).
- `[project] name = "plan-id"` and `[tool.uv.build-backend] module-name = "plan_id"` (same override shape as `blind-review`).
- `mint` prints exactly one line to stdout: the basename. It does not create `docs/plans/`, the plan directory, or any other path.
- `{id}` is eight `secrets.choice` draws from `0123456789abcdefghijklmnopqrstuvwxyz`.
- Runtime dependencies are empty. Dev: pytest only.
- No parse of sibling names. No regex that extracts an id from existing directories. No `test_parse.py`.
- Collision: `{date}-{id}-{slug}-pending` equals an immediate child name of `--plans-dir`. Retry. Cap 16, then exit 1.
- `--plans-dir` set to a path that does not exist ⇒ empty name set, exit 0 if the slug is valid (still print a name). Do not create that path.
- `--date` must match `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`; otherwise exit 1, no stdout basename.
- Slug must match `^[a-z0-9]+(-[a-z0-9]+)*$`; otherwise exit 1, no stdout basename.

## Risks

- A test that calls real `secrets.choice` cannot assert a specific id. Collision and retry-exhausted tests must stub the drawer in `names.py`.
- If stdout is polluted with logs, the create skill will mkdir the wrong name. Only the basename may go to stdout; errors go to stderr.

## Implementation

### Files

- `create-multi-stage-plan/scripts/plan-id/pyproject.toml`
- `create-multi-stage-plan/scripts/plan-id/uv.lock`
- `create-multi-stage-plan/scripts/plan-id/README.md`
- `create-multi-stage-plan/scripts/plan-id/src/plan_id/__init__.py`
- `create-multi-stage-plan/scripts/plan-id/src/plan_id/cli.py`
- `create-multi-stage-plan/scripts/plan-id/src/plan_id/names.py`
- `create-multi-stage-plan/scripts/plan-id/tests/test_mint.py`

### Steps

1. Scaffold like `jp-romaji/scripts/romaji/` and `nuclear-blind-review/scripts/blind-review/`: `requires-python >= 3.11`, `uv_build`, `[project.scripts] plan-id = "plan_id.cli:main"`, `[tool.uv.build-backend] module-name = "plan_id"`, pytest in the dev group. No runtime dependencies.
2. Implement `plan-id mint --plans-dir DIR --slug SLUG [--date YYYY-MM-DD]`:
   - Default `--date` is the machine local calendar date.
   - Validate `--slug` and `--date` as in Invariants.
   - List immediate child names of `--plans-dir` when that path exists (names only; do not parse them).
   - Loop at most 16 times: draw 8 characters with `secrets.choice` from `0123456789abcdefghijklmnopqrstuvwxyz`; candidate = `{date}-{id}-{slug}-pending`; if that string is already a child name, retry; else accept. If all 16 collide, stderr and exit 1.
   - Print the candidate and exit 0.
3. Do not add `list`, `parse`, or `resolve` commands. Put the draw in a one-liner function on `names.py` so tests can stub it.
4. Tests (tmp_path fixtures, no reliance on this repo’s `docs/plans/`):
   - Stub the drawer to return `v1stgxr8`; output is `{--date}-v1stgxr8-{--slug}-pending`.
   - Pre-create that same basename as a directory; stub the drawer to yield the colliding id then `bbbbbb22`; output uses `bbbbbb22`.
   - Stub the drawer to return an id whose constructed basename already exists, 16 times; exit 1, no basename on stdout.
   - Reject slugs `Foo`, `has+plus`, `has_underscore`, `""`.
   - Reject `--date 2026/08/16`.
   - `--plans-dir` points at a nonexistent directory: succeeds, prints a basename, does not create that path.
   - After a successful mint, the printed path does not exist.
   - Files in `--plans-dir` are ignored (only directory names are in the name set).
5. One-paragraph `README.md`: the invoke line `uv run --project <skill-dir>/scripts/plan-id plan-id mint --plans-dir docs/plans --slug <slug>` and that stdout is one basename. No agent protocol.

### Verify

```
uv run --project create-multi-stage-plan/scripts/plan-id pytest
```

Must pass. Smoke, from this repo root (do not keep the name):

```
uv run --project create-multi-stage-plan/scripts/plan-id plan-id mint --plans-dir docs/plans --slug smoke-mint
```

Stdout is one line matching `^[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9a-z]{8}-smoke-mint-pending$`. `docs/plans/` gains no new child.

## Acceptance

- `uv run --project create-multi-stage-plan/scripts/plan-id pytest` is green.
- `pyproject.toml` has no runtime `dependencies` (empty list or omitted).
- There is no `test_parse.py` and no sibling-name regex in `src/`.
- `plan-id mint --help` lists `--plans-dir`, `--slug`, and `--date`.
- A smoke mint prints a `{date}-{id}-{slug}-pending` basename and creates nothing.
- Skill markdown files are untouched in this stage.
