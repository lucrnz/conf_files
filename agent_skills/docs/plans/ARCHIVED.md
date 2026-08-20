# Archived plans

Done plan directories removed from `docs/plans/` via git rm. Each entry's command shows that plan's delete commit.

## 2026-08-15-94xad9m8-nuclear-blind-review-done

**Title:** Nuclear blind review

**Commit:** `3a486df9b87d8e3f0f769f4061523621b3a231ee`

Renamed thermo-nuclear to nuclear-review and split its standards into a code bar and a plan bar. Added nuclear-blind-review: a slash-only isolation skill that reviews through a stripped tree and a fresh subagent. Open the diff for the isolation protocol, bar split, and blind-review CLI contracts the living skills still follow.

```bash
git show 3a486df9b87d8e3f0f769f4061523621b3a231ee
```

## 2026-08-16-6dd9208t-lossless-skill-densify-done

**Title:** Lossless densify of plan-skill prompts

**Commit:** `0ddffd04020540bc7527bcd809614b716dce032d`

Cut tokens from create-multi-stage-plan and implement-pending-plans without changing mint, picker, archive, or status behavior. Open the diff to see which sentences were restatement versus load-bearing.

```bash
git show 0ddffd04020540bc7527bcd809614b716dce032d
```

## 2026-08-16-hh7vjr2b-collision-free-plan-ids-done

**Title:** Collision-free plan directory ids

**Commit:** `3d48fb58a5389c304b1bd7b53ff393e8dc370fa0`

Replaced the shared incrementing plan-directory counter with a minted date-id-slug basename and a picker that matches path, basename, or field. Open the diff for the mint uniqueness rule and the implement selection sentence the skills still point at.

```bash
git show 3d48fb58a5389c304b1bd7b53ff393e8dc370fa0
```

## 2026-08-20-2fpurujv-archive-done-multi-select-done

**Title:** Multi-select for archive-done-plans

**Commit:** `cffb23e25af2a020fd9329b103d450bcc545c623`

Changed archive-done-plans so a picker ask is multi-select with Archive all first, then archives the selected set in basename order. Open the diff for the Archive-all-wins rule and the stop-the-batch-on-index-failure contract.

```bash
git show cffb23e25af2a020fd9329b103d450bcc545c623
```

## 2026-08-20-6z75bga5-archive-done-plans-done

**Title:** Archive done plans

**Commit:** `9b87703b3c2e352debf394a504c0be2c2b019d7b`

Added the archive-done-plans skill: git-rm a finished *-done plan directory and index it in ARCHIVED.md so agents can recover the tree with git show. Open the diff for the two-commit SHA rule and the index entry format.

```bash
git show 9b87703b3c2e352debf394a504c0be2c2b019d7b
```
