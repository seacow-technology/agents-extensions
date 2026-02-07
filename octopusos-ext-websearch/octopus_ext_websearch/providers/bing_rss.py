"""Bing RSS provider implementation."""

from __future__ import annotations

from typing import Dict, List

from bs4 import BeautifulSoup

from .html_search_client import http_get, is_http_url


def search_bing_rss(query: str, max_results: int, language: str) -> List[Dict[str, str]]:
    html = http_get(
        "https://www.bing.com/search",
        {"q": query, "format": "rss", "setlang": language, "count": max(max_results, 1)},
        language,
        check_blocked=False,
    )
    soup = BeautifulSoup(html, "xml")

    results: List[Dict[str, str]] = []
    for item in soup.select("channel > item"):
        title_el = item.find("title")
        link_el = item.find("link")
        desc_el = item.find("description")
        if not title_el or not link_el:
            continue
        url = link_el.text.strip()
        if not is_http_url(url):
            continue
        results.append({
            "title": title_el.text.strip(),
            "url": url,
            "snippet": desc_el.text.strip() if desc_el else "",
            "source": "bing_rss",
            "published_at": (item.find("pubDate").text if item.find("pubDate") else "").strip(),
        })
        if len(results) >= max_results:
            break

    return results
