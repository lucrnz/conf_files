"""POST a URL to v.gd. Logs retries to stderr. Returns a short URL or None."""

from __future__ import annotations

import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CREATE_URL = "https://v.gd/create.php"
SHORTEN_TIMEOUT_SECS = 5.0
RATE_LIMIT_WAIT_SECS = 60
_USER_AGENT = "shorten-url"
_HTTPS_PREFIX = "https://v.gd/"
_HTTP_PREFIX = "http://v.gd/"
_FATAL_HTTP = {400, 406}
_FATAL_CODES = {1, 2}
_RATE_HTTP = 502
_RATE_CODE = 3

_OK = "ok"
_FATAL = "fatal"
_RATE = "rate"
_TRANSIENT = "transient"


def shorten(url: str) -> str | None:
    first = _one(url)
    if first[0] == _OK:
        return first[1]
    if first[0] == _FATAL:
        _log(_message(first))
        return None
    if first[0] == _RATE:
        _log("rate-limited, retrying in 60s")
        time.sleep(RATE_LIMIT_WAIT_SECS)
    else:
        _log("transient error, retrying")
    second = _one(url)
    if second[0] == _OK:
        return second[1]
    _log(_message(second))
    return None


def _one(url: str) -> tuple[str, str | None, str]:
    data = urlencode({"format": "json", "url": url}).encode("ascii")
    request = Request(
        CREATE_URL,
        data=data,
        headers={"User-Agent": _USER_AGENT},
        method="POST",
    )
    try:
        with urlopen(request, timeout=SHORTEN_TIMEOUT_SECS) as resp:
            status = getattr(resp, "status", 200)
            body = resp.read()
    except HTTPError as exc:
        status = exc.code
        try:
            body = exc.read()
        except Exception:
            body = b""
        return _classify(status, body)
    except TimeoutError:
        return (_TRANSIENT, None, "timeout")
    except URLError:
        return (_TRANSIENT, None, "network error")
    return _classify(status, body)


def _classify(status: int, body: bytes) -> tuple[str, str | None, str]:
    parsed = _parse(body)
    if status in _FATAL_HTTP:
        return (_FATAL, None, parsed[2] if parsed[0] == _FATAL else f"HTTP {status}")
    if status == _RATE_HTTP:
        return (_RATE, None, parsed[2] if parsed[0] == _RATE else "rate limited")
    if parsed[0] == _OK:
        if status != 200:
            return (_TRANSIENT, None, f"HTTP {status}")
        return parsed
    if parsed[0] in {_FATAL, _RATE}:
        return parsed
    if status >= 500:
        return (_TRANSIENT, None, parsed[2] or f"HTTP {status}")
    if status != 200:
        return (_TRANSIENT, None, parsed[2] or f"HTTP {status}")
    return parsed


def _parse(body: bytes) -> tuple[str, str | None, str]:
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return (_TRANSIENT, None, "invalid response")
    if not isinstance(data, dict):
        return (_TRANSIENT, None, "invalid response")
    if "errorcode" in data:
        code = data["errorcode"]
        msg = _errormessage(data)
        if code in _FATAL_CODES:
            return (_FATAL, None, msg or f"HTTP {400 if code == 1 else 406}")
        if code == _RATE_CODE:
            return (_RATE, None, msg or "rate limited")
        return (_TRANSIENT, None, msg or "invalid response")
    short = data.get("shorturl")
    if not isinstance(short, str):
        return (_TRANSIENT, None, "invalid response")
    return _validated(short)


def _validated(short: str) -> tuple[str, str | None, str]:
    if any(ch.isspace() for ch in short):
        return (_TRANSIENT, None, "invalid response")
    if short.startswith(_HTTP_PREFIX):
        short = _HTTPS_PREFIX + short[len(_HTTP_PREFIX) :]
    if not short.startswith(_HTTPS_PREFIX):
        return (_TRANSIENT, None, "invalid response")
    path = short[len(_HTTPS_PREFIX) :]
    if not path:
        return (_TRANSIENT, None, "invalid response")
    return (_OK, short, "")


def _errormessage(data: dict) -> str:
    msg = data.get("errormessage")
    if isinstance(msg, str) and msg.strip():
        return msg.strip()
    return ""


def _message(attempt: tuple[str, str | None, str]) -> str:
    kind, _short, msg = attempt
    if msg:
        return msg
    if kind == _RATE:
        return "rate limited"
    if kind == _FATAL:
        return "invalid response"
    return "invalid response"


def _log(message: str) -> None:
    print(f"shorten-url: {message}", file=sys.stderr, flush=True)
