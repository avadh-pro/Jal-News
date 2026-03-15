"""NewsAPI.org fetcher implementing IArticleFetcher via BaseFetcher."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests
from dateutil import parser as dateutil_parser

from src.core.models import Article
from src.fetchers.base import BaseFetcher

logger = logging.getLogger(__name__)

NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"
NEWSAPI_DEFAULT_QUERY = (
    '"health news" OR "medical research" OR "clinical trial" '
    'OR "public health" OR "physiotherapy" OR "healthcare"'
)
NEWSAPI_PAGE_SIZE = 50


def _parse_newsapi_date(date_str: Optional[str]) -> datetime:
    """Parse a date string from NewsAPI response."""
    if not date_str:
        return datetime.now(timezone.utc)
    try:
        dt = dateutil_parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


class NewsAPIFetcher(BaseFetcher):
    """Fetches news articles from NewsAPI.org.

    Args:
        api_key: NewsAPI API key (injected, not read from env).
        query: Custom search query. Defaults to a generic health query.
        domains: Comma-separated domain whitelist (e.g. "techcrunch.com,wired.com").
    """

    def __init__(self, api_key: str, query: str = "", domains: str = "") -> None:
        super().__init__(fetcher_name="NewsAPI")
        self._api_key = api_key
        self._query = query or NEWSAPI_DEFAULT_QUERY
        self._domains = domains

    def _fetch_impl(self) -> list[Article]:
        """Fetch articles from NewsAPI."""
        if not self._api_key:
            logger.warning("No NewsAPI key provided. Skipping NewsAPI.")
            return []

        params: dict[str, str | int] = {
            "q": self._query,
            "sortBy": "publishedAt",
            "pageSize": NEWSAPI_PAGE_SIZE,
            "language": "en",
            "apiKey": self._api_key,
        }

        if self._domains:
            params["domains"] = self._domains

        response = requests.get(NEWSAPI_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            logger.error(
                f"NewsAPI returned error: {data.get('message', 'Unknown error')}"
            )
            return []

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=3)

        articles: list[Article] = []
        for item in data.get("articles", []):
            title = (item.get("title") or "").strip()
            if not title or title == "[Removed]":
                continue

            description = (item.get("description") or "").strip()
            url = (item.get("url") or "").strip()
            if not url:
                continue

            source_name = item.get("source", {}).get("name", "NewsAPI")
            source_id = item.get("source", {}).get("id")
            published_at = _parse_newsapi_date(item.get("publishedAt"))
            image_url = item.get("urlToImage")

            if published_at < cutoff_date:
                continue

            # NewsAPI sources with a non-null source.id are established outlets
            tier = "major-outlet" if source_id else "general"
            weight = 0.9 if source_id else 0.7

            articles.append(
                Article(
                    title=title,
                    description=description,
                    url=url,
                    source_name=source_name,
                    published_at=published_at,
                    image_url=image_url,
                    source_tier=tier,
                    credibility_weight=weight,
                )
            )

        logger.info(
            "NewsAPI: %d raw results, %d after 3-day filter",
            len(data.get("articles", [])), len(articles),
        )
        return articles
