# blind-review

Mechanical helper for `/nuclear-blind-review`. From the repo that contains this skill (follow the symlink):

```
uv run --project <skill-dir>/scripts/blind-review blind-review jobs --repo <repo> --surface changes|codebase|picker [--range S^..E]
uv run --project <skill-dir>/scripts/blind-review blind-review prepare --repo <repo> --surface … --kind code|plan [--plan-dir docs/plans/<dir>] [--parent PARENT] [--bar PATH]…
uv run --project <skill-dir>/scripts/blind-review blind-review cleanup --parent PARENT
```

`prepare` without `--parent` creates the parent with `tempfile.mkdtemp(prefix="nuclear-blind-")` and prints it. `cleanup` deletes that parent only.
