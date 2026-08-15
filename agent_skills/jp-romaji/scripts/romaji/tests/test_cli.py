import json
import subprocess
import sys
from io import StringIO

from romaji.cli import main

SHAPE_LINES = [
    "こんにちは",
    "恋は戦争",
    "コーヒー",
    "してやんよ",
    "I love you 愛してる",
    "学校",
]


def _engine_keys(obj: dict) -> None:
    assert set(obj) >= {"hira", "kana", "romaji", "tokens"}
    assert isinstance(obj["hira"], str)
    assert isinstance(obj["kana"], str)
    assert isinstance(obj["romaji"], str)
    assert isinstance(obj["tokens"], list)
    for tok in obj["tokens"]:
        assert set(tok) >= {"orig", "hira", "kana", "romaji"}
        for key in ("orig", "hira", "kana", "romaji"):
            assert isinstance(tok[key], str)
            assert tok[key] is not None


def test_help_exit_zero(capsys):
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    out = capsys.readouterr().out
    assert "--engine" in out


def test_console_script_help():
    result = subprocess.run(
        ["romaji", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--engine" in result.stdout


def test_default_both_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", StringIO("こんにちは\n"))
    assert main([]) == 0
    rec = json.loads(capsys.readouterr().out)
    assert rec["orig"] == "こんにちは"
    assert "pykakasi" in rec and "cutlet" in rec
    _engine_keys(rec["pykakasi"])
    _engine_keys(rec["cutlet"])


def test_engine_pykakasi_omits_cutlet(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", StringIO("こんにちは\n"))
    assert main(["--engine", "pykakasi"]) == 0
    rec = json.loads(capsys.readouterr().out)
    assert "pykakasi" in rec
    assert "cutlet" not in rec


def test_engine_cutlet_omits_pykakasi(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", StringIO("こんにちは\n"))
    assert main(["--engine", "cutlet"]) == 0
    rec = json.loads(capsys.readouterr().out)
    assert "cutlet" in rec
    assert "pykakasi" not in rec


def test_file_input(tmp_path, capsys):
    path = tmp_path / "in.txt"
    path.write_text("こんにちは\n恋は戦争\n", encoding="utf-8")
    assert main([str(path)]) == 0
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [r["orig"] for r in rows] == ["こんにちは", "恋は戦争"]


def test_empty_lines_skipped(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", StringIO("こんにちは\n\n  \n恋は戦争\n"))
    assert main([]) == 0
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [r["orig"] for r in rows] == ["こんにちは", "恋は戦争"]


def test_json_shape_on_synthetic_lines(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", StringIO("\n".join(SHAPE_LINES) + "\n"))
    assert main([]) == 0
    rows = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert len(rows) == len(SHAPE_LINES)
    for rec, orig in zip(rows, SHAPE_LINES, strict=True):
        assert rec["orig"] == orig
        _engine_keys(rec["pykakasi"])
        _engine_keys(rec["cutlet"])
