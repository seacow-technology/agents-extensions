"""Google provider implementation."""

from __future__ import annotations

from typing import Dict, List

from bs4 import BeautifulSoup

from .html_search_client import http_get, is_http_url, normalize_google_url, BlockedError


def _search_google_html(query: str, max_results: int, language: str) -> List[Dict[str, str]]:
    html = http_get(
        "https://www.google.com/search",
        {"q": query, "hl": language, "num": max(max_results, 1), "safe": "active"},
        language,
    )
    soup = BeautifulSoup(html, "html.parser")
    results: List[Dict[str, str]] = []

    for block in soup.select("div#search div.g, div#rso div.g"):
        link = block.select_one("a[href]")
        title_el = block.select_one("h3")
        if not link or not title_el:
            continue
        url = normalize_google_url((link.get("href") or "").strip())
        if not is_http_url(url):
            continue
        snippet_el = block.select_one("div.VwiC3b, div.IsZvec, span.aCOpRe")
        snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
        results.append({"title": title_el.get_text(" ", strip=True), "url": url, "snippet": snippet, "source": "google_html"})
        if len(results) >= max_results:
            return results

    for title_el in soup.select("h3"):
        parent_link = title_el.find_parent("a", href=True)
        if parent_link is None:
            continue
        url = normalize_google_url((parent_link.get("href") or "").strip())
        if not is_http_url(url):
            continue
        if any(existing["url"] == url for existing in results):
            continue
        results.append({"title": title_el.get_text(" ", strip=True), "url": url, "snippet": "", "source": "google_html"})
        if len(results) >= max_results:
            break

    return results


def _search_google_news_rss(query: str, max_results: int, language: str) -> List[Dict[str, str]]:
    html = http_get(
        "https://news.google.com/rss/search",
        {"q": query, "hl": f"{language}-US", "gl": "US", "ceid": f"US:{language}"},
        language,
        check_blocked=False,
    )
    soup = BeautifulSoup(html, "xml")
    results: List[Dict[str, str]] = []
    for item in soup.select("channel > item"):
        link = (item.find("link").text if item.find("link") else "").strip()
        if not is_http_url(link):
            continue
        title = (item.find("title").text if item.find("title") else "").strip()
        snippet = (item.find("description").text if item.find("description") else "").strip()
        pub_date = (item.find("pubDate").text if item.find("pubDate") else "").strip()
        results.append({
            "title": title,
            "url": link,
            "snippet": snippet,
            "source": "google_news_rss",
            "published_at": pub_date,
        })
        if len(results) >= max_results:
            break
    return results


def search_google(query: str, max_results: int, language: str, google_mode: str = "auto") -> List[Dict[str, str]]:
    mode = (google_mode or "auto").strip().lower()
    if mode not in {"auto", "web_html", "news_rss"}:
        raise ValueError(f"Unsupported GOOGLE_MODE: {google_mode}")
    if mode == "news_rss":
        return _search_google_news_rss(query, max_results, language)
    if mode == "web_html":
        return _search_google_html(query, max_results, language)

    try:
        html_results = _search_google_html(query, max_results, language)
        if html_results:
            return html_results
    except BlockedError:
        pass

    return _search_google_news_rss(query, max_results, language)
