from __future__ import annotations

import json
import sys
from io import StringIO

from ask_user.payload import Answer, encode_answers, loads
from ask_user import cli

VALID = json.dumps(
    {
        "questions": [
            {
                "question": "When does the agent use this?",
                "options": [
                    {"label": "Fallback only", "description": "Native tool when present."},
                    {"label": "Always this skill", "description": "Ignore the native tool."},
                ],
            }
        ]
    }
)

ANSWERS = [
    Answer(question="When does the agent use this?", selected=("Fallback only",), other=None)
]


def test_success_prints_encoded_answers(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    monkeypatch.setattr(cli, "display_available", lambda: True)
    monkeypatch.setattr(cli, "ensure_application", lambda: cli.EXIT_OK)
    monkeypatch.setattr(cli, "run_wizard", lambda payload: ANSWERS)

    assert cli.main([]) == cli.EXIT_OK
    captured = capsys.readouterr()
    assert captured.out == encode_answers(ANSWERS)
    assert captured.err == ""


def test_invalid_json_exit_2(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", StringIO("not-json"))
    called = {"wizard": False}

    def boom(_payload):
        called["wizard"] = True
        return None

    monkeypatch.setattr(cli, "run_wizard", boom)
    assert cli.main([]) == cli.EXIT_USAGE
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err
    assert called["wizard"] is False


def test_reserved_other_exit_2(monkeypatch, capsys) -> None:
    payload = json.dumps(
        {"questions": [{"question": "Q", "options": [{"label": "Other"}]}]}
    )
    monkeypatch.setattr(sys, "stdin", StringIO(payload))
    assert cli.main([]) == cli.EXIT_USAGE
    assert capsys.readouterr().out == ""


def test_extra_argv_exit_2(capsys) -> None:
    assert cli.main(["extra"]) == cli.EXIT_USAGE
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err


def test_no_display_skips_wizard(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    monkeypatch.setattr(cli, "display_available", lambda: False)
    called = {"wizard": False, "app": False}

    def app() -> int:
        called["app"] = True
        return cli.EXIT_OK

    def wizard(_payload):
        called["wizard"] = True
        return ANSWERS

    monkeypatch.setattr(cli, "ensure_application", app)
    monkeypatch.setattr(cli, "run_wizard", wizard)
    assert cli.main([]) == cli.EXIT_NO_DISPLAY
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "no display" in captured.err
    assert called["app"] is False
    assert called["wizard"] is False


def test_cancelled_exit_6(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    monkeypatch.setattr(cli, "display_available", lambda: True)
    monkeypatch.setattr(cli, "ensure_application", lambda: cli.EXIT_OK)
    monkeypatch.setattr(cli, "run_wizard", lambda payload: None)
    assert cli.main([]) == cli.EXIT_CANCELLED
    assert capsys.readouterr().out == ""


def test_success_uses_parsed_payload(monkeypatch) -> None:
    seen = {}

    def wizard(payload):
        seen["payload"] = payload
        return ANSWERS

    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    monkeypatch.setattr(cli, "display_available", lambda: True)
    monkeypatch.setattr(cli, "ensure_application", lambda: cli.EXIT_OK)
    monkeypatch.setattr(cli, "run_wizard", wizard)
    assert cli.main([]) == cli.EXIT_OK
    assert seen["payload"] == loads(VALID)


def test_cli_import_does_not_load_pyside6() -> None:
    sys.modules.pop("ask_user.cli", None)
    before = {name for name in sys.modules if name == "PySide6" or name.startswith("PySide6.")}
    import ask_user.cli as cli_mod

    after = {name for name in sys.modules if name == "PySide6" or name.startswith("PySide6.")}
    assert cli_mod.EXIT_OK == 0
    assert after == before
