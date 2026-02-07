"""Entrypoint for internal web search extension."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from .providers.google import search_google
from .providers.bing_rss import search_bing_rss
from .providers.duckduckgo import search_duckduckgo


@dataclass
class ExtensionWebSearchBackend:
    config: Dict[str, Any]

    def search(
        self,
        engine: str,
        query: str,
        max_results: int,
        language: str = "en",
        google_mode: str = "auto",
    ) -> List[Dict[str, Any]]:
        normalized = (engine or "").strip().lower()
        if normalized in {"google", "googlesearch"}:
            return search_google(query=query, max_results=max_results, language=language, google_mode=google_mode)
        if normalized == "bing":
            return search_bing_rss(query=query, max_results=max_results, language=language)
        if normalized == "duckduckgo":
            return search_duckduckgo(query=query, max_results=max_results, language=language)
        raise ValueError(f"Unsupported search engine: {engine}")


def create_web_search_backend(config: Dict[str, Any]) -> ExtensionWebSearchBackend:
    return ExtensionWebSearchBackend(config=config or {})
