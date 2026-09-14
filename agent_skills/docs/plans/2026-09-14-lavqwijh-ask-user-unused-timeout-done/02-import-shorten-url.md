# Stage 02: Import shorten-url client

## Status
done

## Description

Replace ask-user’s in-process v.gd-only shortener with a hard uv path-dependency on the sibling shorten-url package, and call `shorten_url.client.shorten` from the SSH picker.

## Rationale

The user-facing short URL should get TinyURL when v.gd fails, and that behavior already lives in shorten-url. Importing the client deletes the second implementation.

## Invariants

- `printed = shorten(public) or public` still runs after the public wizard URL is known and before the `ask-user: ` stderr line.
- Total shorten failure still prints the long Cloudflare URL and still starts the picker. It is not exit 4.
- Agents still relay only stderr lines that start with `ask-user: `.
- Desktop Qt still does not shorten anything.
- shorten-url’s client, User-Agent, retry policy, and TinyURL GET are not edited.

## Risks

`uv run --project ask-user` fails if `shorten-url/scripts/shorten-url` is not at the path source. Stage 03 is what makes a one-skill dest copy pull that sibling.

## Implementation

### Files

- `ask-user/scripts/ask-user/pyproject.toml`
- `ask-user/scripts/ask-user/uv.lock`
- `ask-user/scripts/ask-user/src/ask_user/cli.py`
- `ask-user/scripts/ask-user/src/ask_user/shorten.py`
- `ask-user/scripts/ask-user/tests/test_shorten.py`
- `ask-user/scripts/ask-user/tests/test_cli.py`
- `ask-user/README.md`

### Steps

1. In `ask-user/scripts/ask-user/pyproject.toml`, set `requires-python = ">=3.11,<3.15"`. Add `"shorten-url"` to `[project] dependencies`. Add `[tool.uv.sources]` with `shorten-url = { path = "../../../shorten-url/scripts/shorten-url" }`.
2. Relock: `uv lock --project ask-user/scripts/ask-user`.
3. In `ask-user/scripts/ask-user/src/ask_user/cli.py`, change the lazy import inside `run_ssh_picker` from `from ask_user.shorten import shorten` to `from shorten_url.client import shorten`. Leave `printed = shorten(public) or public` and the stderr print as they are.
4. Delete `ask-user/scripts/ask-user/src/ask_user/shorten.py` and `ask-user/scripts/ask-user/tests/test_shorten.py`.
5. In `ask-user/scripts/ask-user/tests/test_cli.py`, retarget every `ask_user.shorten.shorten` monkeypatch to `shorten_url.client.shorten`. Do not add shortener unit tests. Do not change `_FakePicker`’s unused constructor default.
6. In `ask-user/README.md`, update the SSH paragraph so the printed URL is normally a v.gd short link, TinyURL if v.gd cannot create the link, and a long `*.trycloudflare.com` URL if both fail. Do not edit the unused-fuse wait (it is not documented there).

### Verify

From the repo root:

```
uv run --project ask-user/scripts/ask-user --group dev pytest
```

All remaining tests pass. `rg ask_user\\.shorten|from ask_user.shorten` is empty. `uv run --project ask-user/scripts/ask-user python -c 'from shorten_url.client import shorten'` exits 0.

## Acceptance

- `run_ssh_picker` calls `shorten_url.client.shorten`.
- `ask_user/shorten.py` and `tests/test_shorten.py` are gone.
- ask-user’s pyproject requires Python `>=3.11,<3.15` and path-depends on `../../../shorten-url/scripts/shorten-url`.
- README names v.gd, then TinyURL, then the long Cloudflare URL.
- `uv run --project ask-user/scripts/ask-user --group dev pytest` exits 0.
- No new tests under `shorten-url/`.
