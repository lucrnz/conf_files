"""Spawn pnpx/npx untun and parse the public HTTPS origin."""

from __future__ import annotations

import io
import os
import re
import select
import shutil
import signal
import subprocess
import time
from typing import IO, TextIO

ORIGIN_RE = re.compile(r"https://[a-zA-Z0-9.-]+")
ORIGIN_WAIT_SECS = 120.0


class TunnelError(Exception):
    """Could not start a public tunnel."""


class Tunnel:
    def __init__(self, origin: str, proc: subprocess.Popen[str]) -> None:
        self.origin = origin.rstrip("/")
        self._proc = proc

    def close(self) -> None:
        proc = self._proc
        if proc.poll() is not None:
            return
        _stop_group(proc, signal.SIGTERM)
        try:
            proc.wait(timeout=1)
            return
        except subprocess.TimeoutExpired:
            pass
        _stop_group(proc, signal.SIGKILL)
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            return


def find_runner() -> str | None:
    return shutil.which("pnpx") or shutil.which("npx")


def start_tunnel(port: int) -> Tunnel:
    runner = find_runner()
    if runner is None:
        raise TunnelError("no tunnel")
    proc = _spawn(runner, port)
    try:
        origin = _wait_for_origin(proc, ORIGIN_WAIT_SECS)
    except Exception:
        _force_close(proc)
        raise
    return Tunnel(origin, proc)


def _spawn(runner: str, port: int) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["UNTUN_ACCEPT_CLOUDFLARE_NOTICE"] = "1"
    return subprocess.Popen(
        [runner, "untun@latest", "tunnel", f"http://127.0.0.1:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
        env=env,
    )


def _wait_for_origin(proc: subprocess.Popen[str], timeout: float) -> str:
    stream = proc.stdout
    if stream is None:
        raise TunnelError("no tunnel")
    deadline = time.monotonic() + timeout
    buf = ""
    while time.monotonic() < deadline:
        remaining = deadline - time.monotonic()
        line = _read_line(stream, min(0.1, max(remaining, 0.0)))
        if line:
            buf += line
            match = ORIGIN_RE.search(buf)
            if match:
                return match.group(0).rstrip("/")
        elif proc.poll() is not None:
            raise TunnelError("no tunnel")
    raise TunnelError("no tunnel")


def _read_line(stream: IO[str] | TextIO, timeout: float) -> str:
    try:
        stream.fileno()
    except (AttributeError, io.UnsupportedOperation):
        return stream.readline()
    ready, _, _ = select.select([stream], [], [], timeout)
    if not ready:
        return ""
    return stream.readline()


def _stop_group(proc: subprocess.Popen[str], sig: int) -> None:
    try:
        os.killpg(proc.pid, sig)
    except (ProcessLookupError, PermissionError, OSError):
        if sig == signal.SIGTERM:
            proc.terminate()
        else:
            proc.kill()


def _force_close(proc: subprocess.Popen[str]) -> None:
    Tunnel("", proc).close()
