from __future__ import annotations

import json
import sys
import threading
import urllib.error
import urllib.request

from ask_user.payload import Answer, loads
from ask_user.http_wizard import HttpPicker, UnusedTimeout

TOKEN = "ab" * 32
PAYLOAD_TEXT = json.dumps(
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
PAYLOAD = loads(PAYLOAD_TEXT)
COMPLETE = {
    "answers": [
        {
            "question": "When does the agent use this?",
            "selected": ["Fallback only"],
            "other": None,
        }
    ]
}


def _url(port: int, path: str) -> str:
    return f"http://127.0.0.1:{port}{path}"


def _open(port: int, path: str, data: bytes | None = None, method: str | None = None):
    request = urllib.request.Request(
        _url(port, path),
        data=data,
        method=method or ("POST" if data is not None else "GET"),
    )
    if data is not None:
        request.add_header("Content-Type", "application/json")
    return urllib.request.urlopen(request, timeout=2)


def test_bind_returns_ephemeral_port() -> None:
    picker = HttpPicker(PAYLOAD, TOKEN)
    port = picker.bind()
    try:
        assert port > 0
    finally:
        picker.shutdown()


def test_wrong_paths_are_404() -> None:
    picker = HttpPicker(PAYLOAD, TOKEN)
    port = picker.bind()
    picker.serve_in_thread()
    try:
        for path in ("/", f"/t/{TOKEN}x/", f"/t/{TOKEN}/nope"):
            try:
                _open(port, path)
            except urllib.error.HTTPError as exc:
                assert exc.code == 404
            else:
                raise AssertionError(f"expected 404 for {path}")
    finally:
        picker.shutdown()


def test_get_html_contains_sri_and_does_not_open() -> None:
    picker = HttpPicker(PAYLOAD, TOKEN)
    port = picker.bind()
    picker.serve_in_thread()
    try:
        with _open(port, f"/t/{TOKEN}/") as response:
            assert response.status == 200
            html = response.read().decode("utf-8")
        assert "https://unpkg.com/7.css@0.21.1/dist/7.css" in html
        assert (
            'integrity="sha384-WN2QoZVHe/0w3aOmuNlv18gZn4NKrLXxgsUtsLAXPV1zCE/49AFfl07gQ2knrObx"'
            in html
        )
        assert 'crossorigin="anonymous"' in html
        assert "ask-user" in html
        assert picker.opened is False
    finally:
        picker.shutdown()


def test_slashless_redirects() -> None:
    picker = HttpPicker(PAYLOAD, TOKEN)
    port = picker.bind()
    picker.serve_in_thread()
    try:

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        raw = urllib.request.build_opener(NoRedirect)
        try:
            raw.open(_url(port, f"/t/{TOKEN}"), timeout=2)
        except urllib.error.HTTPError as exc:
            assert exc.code == 302
            assert exc.headers["Location"] == f"/t/{TOKEN}/"
        else:
            raise AssertionError("expected 302")
    finally:
        picker.shutdown()


def test_opened_beacon_sets_flag() -> None:
    picker = HttpPicker(PAYLOAD, TOKEN)
    port = picker.bind()
    picker.serve_in_thread()
    try:
        with _open(port, f"/t/{TOKEN}/opened", data=b"") as response:
            assert response.status == 204
        assert picker.opened is True
    finally:
        picker.shutdown()


def test_incomplete_submit_is_400_and_wait_stays() -> None:
    picker = HttpPicker(PAYLOAD, TOKEN)
    port = picker.bind()
    picker.serve_in_thread()
    seen: list[object] = []

    def waiter() -> None:
        try:
            seen.append(picker.wait())
        except UnusedTimeout as exc:
            seen.append(exc)

    thread = threading.Thread(target=waiter)
    thread.start()
    try:
        body = json.dumps(
            {
                "answers": [
                    {
                        "question": "When does the agent use this?",
                        "selected": [],
                        "other": None,
                    }
                ]
            }
        ).encode()
        try:
            _open(port, f"/t/{TOKEN}/submit", data=body)
        except urllib.error.HTTPError as exc:
            assert exc.code == 400
        else:
            raise AssertionError("expected 400")
        thread.join(0.2)
        assert thread.is_alive()
        assert seen == []
    finally:
        picker.shutdown()
        thread.join(1)


def test_complete_submit_returns_answers() -> None:
    picker = HttpPicker(PAYLOAD, TOKEN)
    port = picker.bind()
    picker.serve_in_thread()
    try:
        with _open(
            port, f"/t/{TOKEN}/submit", data=json.dumps(COMPLETE).encode()
        ) as response:
            assert response.status == 200
        answers = picker.wait()
        assert answers == [
            Answer(
                question="When does the agent use this?",
                selected=("Fallback only",),
                other=None,
            )
        ]
    finally:
        picker.shutdown()


def test_cancel_unblocks_with_none() -> None:
    picker = HttpPicker(PAYLOAD, TOKEN)
    port = picker.bind()
    picker.serve_in_thread()
    try:
        with _open(port, f"/t/{TOKEN}/cancel", data=b"") as response:
            assert response.status == 200
        assert picker.wait() is None
    finally:
        picker.shutdown()


def test_unused_timeout_without_opened() -> None:
    picker = HttpPicker(PAYLOAD, TOKEN, unused_timeout_secs=0.05)
    picker.bind()
    picker.serve_in_thread()
    try:
        try:
            picker.wait()
        except UnusedTimeout:
            pass
        else:
            raise AssertionError("expected UnusedTimeout")
    finally:
        picker.shutdown()


def test_opened_then_short_interval_does_not_fire() -> None:
    picker = HttpPicker(PAYLOAD, TOKEN, unused_timeout_secs=0.05)
    port = picker.bind()
    picker.serve_in_thread()
    seen: list[object] = []

    def waiter() -> None:
        try:
            seen.append(("ok", picker.wait()))
        except UnusedTimeout:
            seen.append("timeout")

    thread = threading.Thread(target=waiter)
    thread.start()
    try:
        _open(port, f"/t/{TOKEN}/opened", data=b"")
        thread.join(0.2)
        assert thread.is_alive()
        assert seen == []
        _open(port, f"/t/{TOKEN}/cancel", data=b"")
        thread.join(1)
        assert seen == [("ok", None)]
    finally:
        picker.shutdown()
        thread.join(1)


def test_http_wizard_import_does_not_load_pyside6() -> None:
    sys.modules.pop("ask_user.http_wizard", None)
    before = {name for name in sys.modules if name == "PySide6" or name.startswith("PySide6.")}
    import ask_user.http_wizard as http_mod

    after = {name for name in sys.modules if name == "PySide6" or name.startswith("PySide6.")}
    assert http_mod.DEFAULT_UNUSED_TIMEOUT_SECS == 600.0
    assert after == before
