"""POST a URL to v.gd. Qt-free. Never talks to the picker."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CREATE_URL = "https://v.gd/create.php"
SHORTEN_TIMEOUT_SECS = 5.0
_USER_AGENT = "ask-user"
_HTTPS_PREFIX = "https://v.gd/"
_HTTP_PREFIX = "http://v.gd/"
_FATAL_HTTP = {400, 406}
_FATAL_CODES = {1, 2}

_OK = "ok"
_FATAL = "fatal"
_RETRY = "retry"


def shorten(url: str) -> str | None:
    first = _one(url)
    if first[0] == _OK:
        return first[1]
    if first[0] == _FATAL:
        return None
    second = _one(url)
    if second[0] == _OK:
        return second[1]
    return None


def _one(url: str) -> tuple[str, str | None]:
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
        if status in _FATAL_HTTP:
            return (_FATAL, None)
        if status < 500:
            parsed = _parse(body)
            return parsed if parsed[0] == _FATAL else (_RETRY, None)
        return (_RETRY, None)
    except (URLError, TimeoutError):
        return (_RETRY, None)
    if status in _FATAL_HTTP:
        return (_FATAL, None)
    if status >= 500:
        return (_RETRY, None)
    if status != 200:
        parsed = _parse(body)
        return parsed if parsed[0] == _FATAL else (_RETRY, None)
    return _parse(body)


def _parse(body: bytes) -> tuple[str, str | None]:
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return (_RETRY, None)
    if not isinstance(data, dict):
        return (_RETRY, None)
    if "errorcode" in data:
        code = data["errorcode"]
        if code in _FATAL_CODES:
            return (_FATAL, None)
        return (_RETRY, None)
    short = data.get("shorturl")
    if not isinstance(short, str):
        return (_RETRY, None)
    return _validated(short)


def _validated(short: str) -> tuple[str, str | None]:
    if any(ch.isspace() for ch in short):
        return (_RETRY, None)
    if short.startswith(_HTTP_PREFIX):
        short = _HTTPS_PREFIX + short[len(_HTTP_PREFIX) :]
    if not short.startswith(_HTTPS_PREFIX):
        return (_RETRY, None)
    path = short[len(_HTTPS_PREFIX) :]
    if not path:
        return (_RETRY, None)
    return (_OK, short)
