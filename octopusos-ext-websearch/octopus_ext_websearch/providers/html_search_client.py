"""Shared HTTP and parsing helpers for internal web search providers."""

from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


class BlockedError(Exception):
    """Raised when a challenge/bot page is detected."""


def looks_like_challenge_page(html: str) -> bool:
    normalized = html.lower()
    markers = (
        "enable javascript",
        "unusual traffic",
        "captcha",
        "verify you are human",
        "cloudflare",
        "bot detection",
    )
    return any(marker in normalized for marker in markers)


def http_get(url: str, params: dict, language: str, timeout: int = 30, check_blocked: bool = True) -> str:
    request_url = f"{url}?{urlencode(params, doseq=True)}"
    request = Request(
        request_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": language or "en",
            "Cache-Control": "no-cache",
            "Referer": "https://www.google.com/",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        html = response.read().decode(charset, errors="replace")
    if check_blocked and looks_like_challenge_page(html):
        raise BlockedError(f"Blocked/challenge response from {urlparse(url).netloc}")
    return html


def normalize_google_url(href: str) -> str:
    if href.startswith("/url?"):
        parsed = urlparse(href)
        return parse_qs(parsed.query).get("q", [""])[0]
    return href


def normalize_duckduckgo_url(href: str) -> str:
    candidate = f"https:{href}" if href.startswith("//") else href
    parsed = urlparse(candidate)
    if parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
        target = parse_qs(parsed.query).get("uddg", [""])[0]
        if target:
            return target
    return candidate


def is_http_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


__all__ = [
    "BlockedError",
    "HTTPError",
    "URLError",
    "http_get",
    "normalize_google_url",
    "normalize_duckduckgo_url",
    "is_http_url",
]
