"""argparse CLI: stdin questions JSON, stdout answers JSON."""

from __future__ import annotations

import argparse
import os
import sys

from ask_user.payload import Answer, Payload, PayloadError, encode_answers, loads

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_NO_DISPLAY = 4
EXIT_CANCELLED = 6


def display_available() -> bool:
    if sys.platform.startswith("linux"):
        return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    return True


def ensure_application() -> int:
    try:
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("PySide6 is not available", file=sys.stderr)
        return EXIT_NO_DISPLAY
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv[:1])
        app.setApplicationName("ask-user")
    except Exception as exc:
        print(f"cannot open a window: {exc}", file=sys.stderr)
        return EXIT_NO_DISPLAY
    platform = QGuiApplication.platformName()
    if platform in {"offscreen", "minimal"}:
        print(f"no display ({platform})", file=sys.stderr)
        return EXIT_NO_DISPLAY
    if not QGuiApplication.screens():
        print("no display (no screens)", file=sys.stderr)
        return EXIT_NO_DISPLAY
    return EXIT_OK


def run_wizard(payload: Payload) -> list[Answer] | None:
    from ask_user.wizard import run_wizard as _run

    return _run(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ask-user",
        description="Ask multiple-choice questions in a desktop window.",
    )
    try:
        parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return EXIT_OK
        return int(code)

    text = sys.stdin.read()
    try:
        payload = loads(text)
    except PayloadError as exc:
        print(exc, file=sys.stderr)
        return EXIT_USAGE

    if not display_available():
        print("no display", file=sys.stderr)
        return EXIT_NO_DISPLAY

    app_code = ensure_application()
    if app_code != EXIT_OK:
        return app_code

    answers = run_wizard(payload)
    if answers is None:
        return EXIT_CANCELLED
    sys.stdout.write(encode_answers(answers))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
