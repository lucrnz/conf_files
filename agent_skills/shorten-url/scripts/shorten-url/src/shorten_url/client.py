"""Shorten a URL via v.gd, then TinyURL. Logs failures to stderr."""

from __future__ import annotations

import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CREATE_URL = "https://v.gd/create.php"
TINY_CREATE = "https://tinyurl.com/api-create.php"
SHORTEN_TIMEOUT_SECS = 5.0
_USER_AGENT = "shorten-url"
_VGD_HTTPS = "https://v.gd/"
_VGD_HTTP = "http://v.gd/"
_TINY_HTTPS = "https://tinyurl.com/"
_TINY_HTTP = "http://tinyurl.com/"

_OK = "ok"
_FAIL = "fail"


def shorten(url: str) -> str | None:
    first = _vgd(url)
    if first[0] == _OK:
        return first[1]
    second = _tiny(url)
    if second[0] == _OK:
        return second[1]
    _log(first[2] or second[2] or "invalid response")
    return None


def _vgd(url: str) -> tuple[str, str | None, str]:
    data = urlencode({"format": "json", "url": url}).encode("ascii")
    request = Request(
        CREATE_URL,
        data=data,
        headers={"User-Agent": _USER_AGENT},
        method="POST",
    )
    status, body, err = _http(request)
    if err:
        return (_FAIL, None, err)
    parsed = _parse_vgd(body)
    if parsed[0] == _OK:
        if status != 200:
            return (_FAIL, None, f"HTTP {status}")
        return parsed
    return (_FAIL, None, parsed[2] or (f"HTTP {status}" if status != 200 else "invalid response"))


def _tiny(url: str) -> tuple[str, str | None, str]:
    request = Request(
        f"{TINY_CREATE}?{urlencode({'url': url})}",
        headers={"User-Agent": _USER_AGENT},
    )
    status, body, err = _http(request)
    if err:
        return (_FAIL, None, err)
    if status != 200:
        return (_FAIL, None, f"HTTP {status}")
    try:
        text = body.decode("utf-8").strip()
    except UnicodeDecodeError:
        return (_FAIL, None, "invalid response")
    if not text or text.lower().startswith("error"):
        return (_FAIL, None, text or "invalid response")
    return _validated(text, _TINY_HTTPS, _TINY_HTTP)


def _http(request: Request) -> tuple[int, bytes, str]:
    try:
        with urlopen(request, timeout=SHORTEN_TIMEOUT_SECS) as resp:
            return getattr(resp, "status", 200), resp.read(), ""
    except HTTPError as exc:
        try:
            body = exc.read()
        except Exception:
            body = b""
        return exc.code, body, ""
    except TimeoutError:
        return 0, b"", "timeout"
    except URLError:
        return 0, b"", "network error"


def _parse_vgd(body: bytes) -> tuple[str, str | None, str]:
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        return (_FAIL, None, "invalid response")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        stripped = text.strip()
        return (_FAIL, None, stripped or "invalid response")
    if not isinstance(data, dict):
        return (_FAIL, None, "invalid response")
    if "errorcode" in data:
        msg = data.get("errormessage")
        if isinstance(msg, str) and msg.strip():
            return (_FAIL, None, msg.strip())
        return (_FAIL, None, "invalid response")
    short = data.get("shorturl")
    if not isinstance(short, str):
        return (_FAIL, None, "invalid response")
    return _validated(short, _VGD_HTTPS, _VGD_HTTP)


def _validated(
    short: str, https_prefix: str, http_prefix: str
) -> tuple[str, str | None, str]:
    if any(ch.isspace() for ch in short):
        return (_FAIL, None, "invalid response")
    if short.startswith(http_prefix):
        short = https_prefix + short[len(http_prefix) :]
    if not short.startswith(https_prefix):
        return (_FAIL, None, "invalid response")
    if not short[len(https_prefix) :]:
        return (_FAIL, None, "invalid response")
    return (_OK, short, "")


def _log(message: str) -> None:
    print(f"shorten-url: {message}", file=sys.stderr, flush=True)
