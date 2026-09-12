from __future__ import annotations

import io
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs

from ask_user import shorten

PUBLIC = (
    "https://example.trycloudflare.com/t/"
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef/"
)
SHORT = "https://v.gd/R709K6"


class FakeResponse:
    def __init__(self, body: bytes, status: int = 200) -> None:
        self._body = body
        self.status = status

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None


def _http_error(code: int, body: bytes) -> HTTPError:
    return HTTPError(shorten.CREATE_URL, code, "err", hdrs=None, fp=io.BytesIO(body))


def _queue_urlopen(monkeypatch, items: list[object]) -> list[tuple[object, float | None]]:
    calls: list[tuple[object, float | None]] = []

    def fake_urlopen(request, timeout=None):
        calls.append((request, timeout))
        item = items.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    monkeypatch.setattr(shorten, "urlopen", fake_urlopen)
    return calls


def test_success_one_call(monkeypatch) -> None:
    calls = _queue_urlopen(
        monkeypatch, [FakeResponse(json.dumps({"shorturl": SHORT}).encode())]
    )
    assert shorten.shorten(PUBLIC) == SHORT
    assert len(calls) == 1
    request, timeout = calls[0]
    assert request.full_url == "https://v.gd/create.php"
    assert request.get_method() == "POST"
    assert timeout == 5.0
    body = request.data.decode("ascii")
    fields = parse_qs(body, keep_blank_values=True)
    assert fields == {"format": ["json"], "url": [PUBLIC]}
    assert "shorturl" not in body
    assert "logstats" not in body
    assert request.get_header("User-agent") == "ask-user"


def test_rewrites_http_shorturl(monkeypatch) -> None:
    _queue_urlopen(
        monkeypatch,
        [FakeResponse(json.dumps({"shorturl": "http://v.gd/R709K6"}).encode())],
    )
    assert shorten.shorten(PUBLIC) == SHORT


def test_urlerror_then_success(monkeypatch) -> None:
    calls = _queue_urlopen(
        monkeypatch,
        [
            URLError("down"),
            FakeResponse(json.dumps({"shorturl": SHORT}).encode()),
        ],
    )
    assert shorten.shorten(PUBLIC) == SHORT
    assert len(calls) == 2


def test_timeout_then_success(monkeypatch) -> None:
    calls = _queue_urlopen(
        monkeypatch,
        [
            TimeoutError("timed out"),
            FakeResponse(json.dumps({"shorturl": SHORT}).encode()),
        ],
    )
    assert shorten.shorten(PUBLIC) == SHORT
    assert len(calls) == 2


def test_two_failures_return_none(monkeypatch) -> None:
    calls = _queue_urlopen(
        monkeypatch, [URLError("down"), URLError("still down")]
    )
    assert shorten.shorten(PUBLIC) is None
    assert len(calls) == 2


def test_http_400_error_code_1_no_retry(monkeypatch) -> None:
    body = json.dumps({"errorcode": 1, "errormessage": "bad url"}).encode()
    calls = _queue_urlopen(monkeypatch, [_http_error(400, body)])
    assert shorten.shorten(PUBLIC) is None
    assert len(calls) == 1


def test_json_error_code_1_on_200_no_retry(monkeypatch) -> None:
    body = json.dumps({"errorcode": 1, "errormessage": "bad url"}).encode()
    calls = _queue_urlopen(monkeypatch, [FakeResponse(body)])
    assert shorten.shorten(PUBLIC) is None
    assert len(calls) == 1


def test_http_502_then_success(monkeypatch) -> None:
    calls = _queue_urlopen(
        monkeypatch,
        [
            _http_error(502, json.dumps({"errorcode": 3}).encode()),
            FakeResponse(json.dumps({"shorturl": SHORT}).encode()),
        ],
    )
    assert shorten.shorten(PUBLIC) == SHORT
    assert len(calls) == 2


def test_invalid_shorturl_retries_then_none(monkeypatch) -> None:
    calls = _queue_urlopen(
        monkeypatch,
        [
            FakeResponse(json.dumps({"shorturl": "https://example.com/x"}).encode()),
            FakeResponse(json.dumps({"shorturl": "https://example.com/x"}).encode()),
        ],
    )
    assert shorten.shorten(PUBLIC) is None
    assert len(calls) == 2


def test_import_does_not_load_pyside6() -> None:
    sys.modules.pop("ask_user.shorten", None)
    before = {name for name in sys.modules if name == "PySide6" or name.startswith("PySide6.")}
    import ask_user.shorten as shorten_mod

    after = {name for name in sys.modules if name == "PySide6" or name.startswith("PySide6.")}
    assert shorten_mod.CREATE_URL == "https://v.gd/create.php"
    assert shorten_mod.SHORTEN_TIMEOUT_SECS == 5.0
    assert after == before
