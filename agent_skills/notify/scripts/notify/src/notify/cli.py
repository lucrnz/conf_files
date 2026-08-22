"""argparse CLI: send one desktop notification."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_UNSUPPORTED = 3
EXIT_NO_HELPER = 4
EXIT_HELPER = 5

OSASCRIPT = """on run argv
display notification (item 2 of argv) with title (item 1 of argv) sound name "default"
delay 0.5
end run
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="notify",
        description="Send one desktop notification.",
    )
    parser.add_argument("--title", required=True)
    parser.add_argument("--message", required=True)
    args = parser.parse_args(argv)
    title = args.title.strip()
    message = args.message.strip()
    if not title or not message:
        print("title and message must be non-empty", file=sys.stderr)
        return EXIT_USAGE
    return send(title, message)


def send(title: str, message: str) -> int:
    if sys.platform == "darwin":
        return _darwin(title, message)
    if sys.platform.startswith("linux"):
        return _linux(title, message)
    print(f"unsupported OS: {sys.platform}", file=sys.stderr)
    return EXIT_UNSUPPORTED


def _run(argv: list[str], stdin: str | None = None) -> int:
    result = subprocess.run(argv, input=stdin, capture_output=True, text=True)
    if result.returncode == 0:
        return EXIT_OK
    text = result.stderr if result.stderr else result.stdout
    if text:
        sys.stderr.write(text)
        if not text.endswith("\n"):
            sys.stderr.write("\n")
    return EXIT_HELPER


def _osascript() -> str | None:
    found = shutil.which("osascript")
    if found:
        return found
    fallback = Path("/usr/bin/osascript")
    if fallback.is_file():
        return str(fallback)
    return None


def _darwin(title: str, message: str) -> int:
    notifier = shutil.which("terminal-notifier")
    if notifier:
        return _run(
            [notifier, "-title", title, "-message", message, "-sound", "default"]
        )
    osa = _osascript()
    if osa is None:
        print("no notification helper found", file=sys.stderr)
        return EXIT_NO_HELPER
    return _run([osa, "-", title, message], stdin=OSASCRIPT)


def _linux(title: str, message: str) -> int:
    notify_send = shutil.which("notify-send")
    if notify_send:
        return _run(
            [notify_send, "-a", "notify-me", "-u", "normal", "--", title, message]
        )
    gdbus = shutil.which("gdbus")
    if gdbus:
        return _run(
            [
                gdbus,
                "call",
                "--session",
                "--dest",
                "org.freedesktop.Notifications",
                "--object-path",
                "/org/freedesktop/Notifications",
                "--method",
                "org.freedesktop.Notifications.Notify",
                "notify-me",
                "0",
                "",
                title,
                message,
                "[]",
                "{}",
                "-1",
            ]
        )
    print("no notification helper found", file=sys.stderr)
    return EXIT_NO_HELPER


if __name__ == "__main__":
    raise SystemExit(main())
