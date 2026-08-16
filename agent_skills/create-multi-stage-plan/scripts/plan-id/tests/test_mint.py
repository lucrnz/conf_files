from __future__ import annotations

from pathlib import Path

import pytest

from plan_id import cli
from plan_id.names import MintError, mint


def test_stubbed_id_missing_plans_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("plan_id.names.draw_id", lambda: "v1stgxr8")
    missing = tmp_path / "nope"
    out = mint(missing, "checkout-rewrite", "2026-08-16")
    assert out == "2026-08-16-v1stgxr8-checkout-rewrite-pending"
    assert not missing.exists()


def test_collision_retries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ids = iter(["aaaaaaaa", "bbbbbb22"])
    monkeypatch.setattr("plan_id.names.draw_id", lambda: next(ids))
    (tmp_path / "2026-08-16-aaaaaaaa-other-pending").mkdir()
    out = mint(tmp_path, "other", "2026-08-16")
    assert out == "2026-08-16-bbbbbb22-other-pending"


def test_collision_exhausted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("plan_id.names.draw_id", lambda: "aaaaaaaa")
    (tmp_path / "2026-08-16-aaaaaaaa-foo-pending").mkdir()
    with pytest.raises(MintError, match="unique basename"):
        mint(tmp_path, "foo", "2026-08-16")


def test_rejects_slugs(tmp_path: Path) -> None:
    for slug in ("Foo", "has+plus", "has_underscore", ""):
        with pytest.raises(MintError, match="invalid slug"):
            mint(tmp_path, slug, "2026-08-16")


def test_rejects_date(tmp_path: Path) -> None:
    with pytest.raises(MintError, match="invalid date"):
        mint(tmp_path, "ok-slug", "2026/08/16")


def test_ignores_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("plan_id.names.draw_id", lambda: "v1stgxr8")
    (tmp_path / "2026-08-16-v1stgxr8-foo-pending").write_text("not a dir\n")
    out = mint(tmp_path, "foo", "2026-08-16")
    assert out == "2026-08-16-v1stgxr8-foo-pending"


def test_does_not_create_printed_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("plan_id.names.draw_id", lambda: "v1stgxr8")
    name = mint(tmp_path, "foo", "2026-08-16")
    assert not (tmp_path / name).exists()


def test_cli_prints_basename(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("plan_id.names.draw_id", lambda: "v1stgxr8")
    code = cli.main(["mint", "--plans-dir", str(tmp_path), "--slug", "foo", "--date", "2026-08-16"])
    assert code == 0
    assert capsys.readouterr().out == "2026-08-16-v1stgxr8-foo-pending\n"


def test_cli_exhausted_no_stdout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("plan_id.names.draw_id", lambda: "aaaaaaaa")
    (tmp_path / "2026-08-16-aaaaaaaa-foo-pending").mkdir()
    code = cli.main(["mint", "--plans-dir", str(tmp_path), "--slug", "foo", "--date", "2026-08-16"])
    assert code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "unique basename" in captured.err


def test_cli_help() -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["mint", "--help"])
    assert exc.value.code == 0
