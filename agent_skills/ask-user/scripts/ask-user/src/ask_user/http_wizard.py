"""Loopback HTTP picker: token routes, unused fuse, 7.css wizard page."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ask_user.payload import Answer, Payload, first_incomplete

TEMPLATE_PATH = Path(__file__).resolve().parent / "static" / "wizard.html"
DEFAULT_UNUSED_TIMEOUT_SECS = 600.0


class UnusedTimeout(Exception):
    """Unused fuse fired before the opened beacon."""


def _payload_object(payload: Payload) -> dict[str, Any]:
    return {
        "questions": [
            {
                "question": question.question,
                "options": [
                    {"label": option.label, "description": option.description}
                    for option in question.options
                ],
                "multi_select": question.multi_select,
            }
            for question in payload.questions
        ]
    }


def render_html(payload: Payload, token: str) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    payload_json = json.dumps(_payload_object(payload), ensure_ascii=False).replace(
        "<", "\\u003c"
    )
    token_json = json.dumps(token)
    return template.replace("__ASK_USER_PAYLOAD__", payload_json, 1).replace(
        "__ASK_USER_TOKEN__", token_json, 1
    )


def _answers_from_body(payload: Payload, raw: bytes) -> list[Answer] | None:
    try:
        data = json.loads(raw.decode("utf-8") or "")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    items = data.get("answers")
    if not isinstance(items, list) or len(items) != len(payload.questions):
        return None
    answers: list[Answer] = []
    for question, item in zip(payload.questions, items, strict=True):
        if not isinstance(item, dict):
            return None
        selected_raw = item.get("selected", [])
        if not isinstance(selected_raw, list) or not all(
            isinstance(label, str) for label in selected_raw
        ):
            return None
        other_raw = item.get("other", None)
        if other_raw is not None and not isinstance(other_raw, str):
            return None
        other = other_raw.strip() if isinstance(other_raw, str) else None
        if other == "":
            other = None
        answers.append(
            Answer(
                question=question.question,
                selected=tuple(selected_raw),
                other=other,
            )
        )
    return answers


class HttpPicker:
    def __init__(
        self,
        payload: Payload,
        token: str,
        unused_timeout_secs: float = DEFAULT_UNUSED_TIMEOUT_SECS,
    ) -> None:
        self._payload = payload
        self._token = token
        self._unused_timeout_secs = unused_timeout_secs
        self._html = render_html(payload, token)
        self._prefix = f"/t/{token}"
        self._lock = threading.Lock()
        self._opened = False
        self._unused_fired = False
        self._answers: list[Answer] | None = None
        self._done = threading.Event()
        self._closed = False
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._unused_timer: threading.Timer | None = None

    @property
    def opened(self) -> bool:
        return self._opened

    def bind(self) -> int:
        if self._server is not None:
            return int(self._server.server_address[1])
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        return int(self._server.server_address[1])

    def serve_in_thread(self) -> None:
        if self._server is None:
            self.bind()
        assert self._server is not None
        if self._thread is None:
            self._thread = threading.Thread(
                target=self._serve,
                name="ask-user-http",
                daemon=True,
            )
            self._thread.start()
        if self._unused_timer is None:
            timer = threading.Timer(self._unused_timeout_secs, self._on_unused)
            timer.daemon = True
            self._unused_timer = timer
            timer.start()

    def wait(self) -> list[Answer] | None:
        self._done.wait()
        if self._unused_fired:
            raise UnusedTimeout
        return self._answers

    def shutdown(self) -> None:
        timer: threading.Timer | None
        server: ThreadingHTTPServer | None
        thread: threading.Thread | None
        with self._lock:
            already = self._closed
            self._closed = True
            timer = self._unused_timer
            server = self._server
            thread = self._thread
        if timer is not None:
            timer.cancel()
        if not already and server is not None:
            if thread is not None:
                server.shutdown()
            server.server_close()
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=2)
        self._done.set()

    def _serve(self) -> None:
        assert self._server is not None
        self._server.serve_forever(poll_interval=0.05)

    def _stop_later(self) -> None:
        threading.Thread(target=self.shutdown, name="ask-user-stop", daemon=True).start()

    def _on_unused(self) -> None:
        with self._lock:
            if self._opened or self._closed:
                return
            self._unused_fired = True
        self._done.set()
        self._stop_later()

    def _mark_opened(self) -> None:
        with self._lock:
            self._opened = True
            timer = self._unused_timer
        if timer is not None:
            timer.cancel()

    def _finish(self, answers: list[Answer] | None) -> None:
        with self._lock:
            if self._done.is_set():
                return
            self._answers = answers
        self._done.set()
        self._stop_later()

    def _route(self, path: str) -> str | None:
        parsed = urlparse(path)
        route = parsed.path
        prefix = self._prefix
        if route == prefix:
            return "slashless"
        if route == prefix + "/":
            return "html"
        if route == prefix + "/opened":
            return "opened"
        if route == prefix + "/submit":
            return "submit"
        if route == prefix + "/cancel":
            return "cancel"
        return None

    def _handler(self) -> type[BaseHTTPRequestHandler]:
        picker = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                return

            def do_GET(self) -> None:
                kind = picker._route(self.path)
                if kind == "slashless":
                    self.send_response(302)
                    self.send_header("Location", picker._prefix + "/")
                    self.end_headers()
                    return
                if kind != "html":
                    self.send_error(404)
                    return
                body = picker._html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self) -> None:
                kind = picker._route(self.path)
                if kind == "opened":
                    picker._mark_opened()
                    self.send_response(204)
                    self.end_headers()
                    return
                if kind == "cancel":
                    picker._finish(None)
                    self.send_response(200)
                    self.end_headers()
                    return
                if kind != "submit":
                    self.send_error(404)
                    return
                length = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(length) if length else b""
                answers = _answers_from_body(picker._payload, raw)
                if answers is None:
                    self.send_error(400)
                    return
                states = [(answer.selected, answer.other) for answer in answers]
                if first_incomplete(states) is not None:
                    self.send_response(400)
                    self.end_headers()
                    return
                picker._finish(answers)
                self.send_response(200)
                self.end_headers()

        return Handler
