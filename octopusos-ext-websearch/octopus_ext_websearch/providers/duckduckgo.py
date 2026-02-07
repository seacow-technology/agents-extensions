"""DuckDuckGo HTML provider implementation."""

from __future__ import annotations

from typing import Dict, List

from bs4 import BeautifulSoup

from .html_search_client import http_get, is_http_url, normalize_duckduckgo_url


def search_duckduckgo(query: str, max_results: int, language: str) -> List[Dict[str, str]]:
    html = http_get(
        "https://html.duckduckgo.com/html/",
        {"q": query, "kl": f"{language}-{language}" if language else "wt-wt"},
        language,
    )
    soup = BeautifulSoup(html, "html.parser")

    results: List[Dict[str, str]] = []
    for block in soup.select("div.result"):
        link = block.select_one("a.result__a[href]") or block.select_one("a[href]")
        if not link:
            continue
        url = normalize_duckduckgo_url((link.get("href") or "").strip())
        if not is_http_url(url):
            continue
        snippet_el = block.select_one("a.result__snippet, div.result__snippet")
        snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
        results.append({"title": link.get_text(" ", strip=True), "url": url, "snippet": snippet, "source": "duckduckgo_html"})
        if len(results) >= max_results:
            break

    return results
