from __future__ import annotations

import io
import sys

import pytest

from ask_user import tunnel


@pytest.fixture(autouse=True)
def no_real_killpg(monkeypatch) -> None:
    def missing(*_args, **_kwargs) -> None:
        raise ProcessLookupError

    monkeypatch.setattr(tunnel.os, "killpg", missing)


def test_find_runner_prefers_pnpx(monkeypatch) -> None:
    monkeypatch.setattr(
        tunnel.shutil,
        "which",
        lambda name: {"pnpx": "/bin/pnpx", "npx": "/bin/npx"}.get(name),
    )
    assert tunnel.find_runner() == "/bin/pnpx"


def test_find_runner_falls_back_to_npx(monkeypatch) -> None:
    monkeypatch.setattr(
        tunnel.shutil,
        "which",
        lambda name: "/bin/npx" if name == "npx" else None,
    )
    assert tunnel.find_runner() == "/bin/npx"


def test_find_runner_none(monkeypatch) -> None:
    monkeypatch.setattr(tunnel.shutil, "which", lambda name: None)
    assert tunnel.find_runner() is None


class FakeProc:
    def __init__(self, lines: list[str], *, exit_immediately: bool = False) -> None:
        self.stdout = io.StringIO("".join(lines))
        self.pid = 4242
        self.returncode = 0 if exit_immediately else None
        self.terminated = False
        self.killed = False

    def poll(self) -> int | None:
        return self.returncode

    def terminate(self) -> None:
        self.terminated = True
        self.returncode = 0

    def kill(self) -> None:
        self.killed = True
        self.returncode = 9

    def wait(self, timeout: float | None = None) -> int:
        if self.returncode is None:
            self.returncode = 0
        return self.returncode


def test_start_tunnel_parses_origin(monkeypatch) -> None:
    spawned: list[tuple[str, int]] = []

    def spawn(runner: str, port: int) -> FakeProc:
        spawned.append((runner, port))
        return FakeProc(["◐ starting\n", "Tunnel ready at https://abc.trycloudflare.com\n"])

    monkeypatch.setattr(tunnel, "find_runner", lambda: "/usr/bin/pnpx")
    monkeypatch.setattr(tunnel, "_spawn", spawn)
    result = tunnel.start_tunnel(9999)
    assert result.origin == "https://abc.trycloudflare.com"
    assert spawned == [("/usr/bin/pnpx", 9999)]


def test_spawn_uses_untun_and_notice(monkeypatch) -> None:
    seen: dict[str, object] = {}

    def fake_popen(argv, **kwargs):
        seen["argv"] = argv
        seen["env"] = kwargs.get("env")
        return FakeProc(["Tunnel ready at https://abc.trycloudflare.com\n"])

    monkeypatch.setattr(tunnel.subprocess, "Popen", fake_popen)
    proc = tunnel._spawn("/usr/bin/pnpx", 8080)
    assert seen["argv"] == [
        "/usr/bin/pnpx",
        "untun@latest",
        "tunnel",
        "http://127.0.0.1:8080",
    ]
    env = seen["env"]
    assert isinstance(env, dict)
    assert env["UNTUN_ACCEPT_CLOUDFLARE_NOTICE"] == "1"
    assert proc.pid == 4242


def test_start_tunnel_timeout_closes_child(monkeypatch) -> None:
    proc = FakeProc([])

    monkeypatch.setattr(tunnel, "find_runner", lambda: "/usr/bin/npx")
    monkeypatch.setattr(tunnel, "_spawn", lambda runner, port: proc)
    monkeypatch.setattr(tunnel, "ORIGIN_WAIT_SECS", 0.05)
    with pytest.raises(tunnel.TunnelError):
        tunnel.start_tunnel(1)
    assert proc.terminated or proc.returncode is not None


def test_close_is_called_on_failure(monkeypatch) -> None:
    proc = FakeProc([])
    monkeypatch.setattr(tunnel, "find_runner", lambda: "/usr/bin/npx")
    monkeypatch.setattr(tunnel, "_spawn", lambda runner, port: proc)

    def boom(proc_arg, timeout):
        raise tunnel.TunnelError("no tunnel")

    monkeypatch.setattr(tunnel, "_wait_for_origin", boom)
    with pytest.raises(tunnel.TunnelError):
        tunnel.start_tunnel(2)
    assert proc.terminated or proc.killed or proc.returncode is not None


def test_tunnel_import_does_not_load_pyside6() -> None:
    sys.modules.pop("ask_user.tunnel", None)
    before = {name for name in sys.modules if name == "PySide6" or name.startswith("PySide6.")}
    import ask_user.tunnel as tunnel_mod

    after = {name for name in sys.modules if name == "PySide6" or name.startswith("PySide6.")}
    assert tunnel_mod.ORIGIN_WAIT_SECS == 120.0
    assert after == before
