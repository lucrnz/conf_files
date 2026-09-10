from __future__ import annotations

import json
import sys
from io import StringIO

import pytest

from ask_user.payload import Answer, encode_answers, loads
from ask_user import cli

SSH_KEYS = ("SSH_CONNECTION", "SSH_CLIENT", "SSH_TTY")


@pytest.fixture(autouse=True)
def clear_ssh_env(monkeypatch) -> None:
    for key in SSH_KEYS:
        monkeypatch.delenv(key, raising=False)

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


def _ssh_skips_qt(monkeypatch, capsys, **env: str) -> None:
    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    called = {"wizard": False, "app": False}

    def app() -> int:
        called["app"] = True
        return cli.EXIT_OK

    def wizard(_payload):
        called["wizard"] = True
        return ANSWERS

    for key, value in env.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr("ask_user.tunnel.find_runner", lambda: None)
    monkeypatch.setattr(cli, "ensure_application", app)
    monkeypatch.setattr(cli, "run_wizard", wizard)
    assert cli.main([]) == cli.EXIT_NO_DISPLAY
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "no tunnel" in captured.err
    assert called["app"] is False
    assert called["wizard"] is False


def test_ssh_connection_loopback_skips_qt(monkeypatch, capsys) -> None:
    _ssh_skips_qt(monkeypatch, capsys, SSH_CONNECTION="127.0.0.1 1 127.0.0.1 2222")


def test_ssh_tty_only_skips_qt(monkeypatch, capsys) -> None:
    _ssh_skips_qt(monkeypatch, capsys, SSH_TTY="/dev/ttys003")


def test_ssh_client_only_skips_qt(monkeypatch, capsys) -> None:
    _ssh_skips_qt(monkeypatch, capsys, SSH_CLIENT="127.0.0.1 55766 2222")


def test_empty_ssh_vars_are_not_ssh(monkeypatch, capsys) -> None:
    monkeypatch.setenv("SSH_CONNECTION", "")
    monkeypatch.setenv("SSH_CLIENT", "")
    monkeypatch.setenv("SSH_TTY", "")
    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    monkeypatch.setattr(cli, "display_available", lambda: False)
    called = {"wizard": False}

    def wizard(_payload):
        called["wizard"] = True
        return ANSWERS

    monkeypatch.setattr(cli, "run_wizard", wizard)
    assert cli.main([]) == cli.EXIT_NO_DISPLAY
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "no display" in captured.err
    assert called["wizard"] is False


def test_ssh_patched_picker_success(monkeypatch, capsys) -> None:
    monkeypatch.setenv("SSH_TTY", "/dev/ttys003")
    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    monkeypatch.setattr(cli, "run_ssh_picker", lambda payload: ANSWERS)
    called = {"wizard": False}

    def wizard(_payload):
        called["wizard"] = True
        return ANSWERS

    monkeypatch.setattr(cli, "run_wizard", wizard)
    assert cli.main([]) == cli.EXIT_OK
    captured = capsys.readouterr()
    assert captured.out == encode_answers(ANSWERS)
    assert called["wizard"] is False


def test_ssh_patched_picker_cancelled(monkeypatch, capsys) -> None:
    monkeypatch.setenv("SSH_CLIENT", "10.0.0.1 1 10.0.0.2 22")
    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    monkeypatch.setattr(cli, "run_ssh_picker", lambda payload: None)
    assert cli.main([]) == cli.EXIT_CANCELLED
    assert capsys.readouterr().out == ""


class _FakeTunnel:
    origin = "https://example.trycloudflare.com"

    def close(self) -> None:
        return None


class _FakePicker:
    last_token = ""

    def __init__(self, payload, token, unused_timeout_secs=600) -> None:
        self.payload = payload
        _FakePicker.last_token = token

    def bind(self) -> int:
        return 12345

    def serve_in_thread(self) -> None:
        return None

    def wait(self):
        return ANSWERS

    def shutdown(self) -> None:
        return None


class _TimeoutPicker(_FakePicker):
    def wait(self):
        from ask_user.http_wizard import UnusedTimeout

        raise UnusedTimeout


class _CancelPicker(_FakePicker):
    def wait(self):
        return None


class _BindRecorder(_FakePicker):
    bound = False

    def bind(self) -> int:
        _BindRecorder.bound = True
        return 12345


def test_ssh_mocked_tunnel_success(monkeypatch, capsys) -> None:
    monkeypatch.setenv("SSH_TTY", "/dev/ttys003")
    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    monkeypatch.setattr("ask_user.tunnel.find_runner", lambda: "/usr/bin/pnpx")
    monkeypatch.setattr("ask_user.tunnel.start_tunnel", lambda port: _FakeTunnel())
    monkeypatch.setattr("ask_user.http_wizard.HttpPicker", _FakePicker)
    assert cli.main([]) == cli.EXIT_OK
    captured = capsys.readouterr()
    assert captured.out == encode_answers(ANSWERS)
    lines = [line for line in captured.err.splitlines() if line.startswith("ask-user: ")]
    assert len(lines) == 1
    url = lines[0].removeprefix("ask-user: ")
    assert url.startswith("https://example.trycloudflare.com/t/")
    assert url.endswith("/")
    token = url.rstrip("/").rsplit("/", 1)[-1]
    assert len(token) == 64
    assert all(c in "0123456789abcdef" for c in token)
    assert "127.0.0.1" not in captured.err


def test_ssh_mocked_unused_timeout(monkeypatch, capsys) -> None:
    monkeypatch.setenv("SSH_TTY", "/dev/ttys003")
    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    monkeypatch.setattr("ask_user.tunnel.find_runner", lambda: "/usr/bin/pnpx")
    monkeypatch.setattr("ask_user.tunnel.start_tunnel", lambda port: _FakeTunnel())
    monkeypatch.setattr("ask_user.http_wizard.HttpPicker", _TimeoutPicker)
    assert cli.main([]) == cli.EXIT_NO_DISPLAY
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "not opened" in captured.err


def test_ssh_mocked_cancel(monkeypatch, capsys) -> None:
    monkeypatch.setenv("SSH_TTY", "/dev/ttys003")
    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    monkeypatch.setattr("ask_user.tunnel.find_runner", lambda: "/usr/bin/pnpx")
    monkeypatch.setattr("ask_user.tunnel.start_tunnel", lambda port: _FakeTunnel())
    monkeypatch.setattr("ask_user.http_wizard.HttpPicker", _CancelPicker)
    assert cli.main([]) == cli.EXIT_CANCELLED
    assert capsys.readouterr().out == ""


def test_ssh_no_runner_does_not_bind(monkeypatch, capsys) -> None:
    _BindRecorder.bound = False
    monkeypatch.setenv("SSH_TTY", "/dev/ttys003")
    monkeypatch.setattr(sys, "stdin", StringIO(VALID))
    monkeypatch.setattr("ask_user.tunnel.find_runner", lambda: None)
    monkeypatch.setattr("ask_user.http_wizard.HttpPicker", _BindRecorder)
    assert cli.main([]) == cli.EXIT_NO_DISPLAY
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "no tunnel" in captured.err
    assert _BindRecorder.bound is False
