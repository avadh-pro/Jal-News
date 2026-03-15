"""RSS feed fetcher implementing IArticleFetcher via BaseFetcher."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import feedparser
from dateutil import parser as dateutil_parser

from src.core.models import Article
from src.fetchers.base import BaseFetcher

logger = logging.getLogger(__name__)


def _parse_published_date(entry: dict) -> Optional[datetime]:
    """Parse the published date from an RSS entry."""
    date_fields = ["published", "updated", "created"]
    for field in date_fields:
        raw = entry.get(field)
        if raw:
            try:
                dt = dateutil_parser.parse(raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, TypeError):
                continue

    # Try struct_time fields
    for field in ["published_parsed", "updated_parsed", "created_parsed"]:
        parsed = entry.get(field)
        if parsed:
            try:
                from calendar import timegm

                return datetime.fromtimestamp(timegm(parsed), tz=timezone.utc)
            except (ValueError, TypeError, OverflowError):
                continue

    return None


def _extract_image_url(entry: dict) -> Optional[str]:
    """Extract image URL from RSS entry if available."""
    # Check media_content
    media = entry.get("media_content", [])
    if media and isinstance(media, list):
        for m in media:
            url = m.get("url", "")
            if url and any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                return url

    # Check media_thumbnail
    thumbnails = entry.get("media_thumbnail", [])
    if thumbnails and isinstance(thumbnails, list):
        return thumbnails[0].get("url")

    # Check enclosures
    enclosures = entry.get("enclosures", [])
    if enclosures and isinstance(enclosures, list):
        for enc in enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href") or enc.get("url")

    return None


def _entry_to_article(
    entry: dict,
    source_name: str,
    source_tier: str = "general",
    credibility_weight: float = 1.0,
) -> Optional[Article]:
    """Convert an RSS feed entry to an Article object."""
    title = entry.get("title", "").strip()
    if not title:
        return None

    description = entry.get("summary", "") or entry.get("description", "")
    description = description.strip()

    link = entry.get("link", "").strip()
    if not link:
        return None

    published_at = _parse_published_date(entry)
    if published_at is None:
        published_at = datetime.now(timezone.utc)

    image_url = _extract_image_url(entry)

    return Article(
        title=title,
        description=description,
        url=link,
        source_name=source_name,
        published_at=published_at,
        image_url=image_url,
        source_tier=source_tier,
        credibility_weight=credibility_weight,
    )


class RSSFetcher(BaseFetcher):
    """Fetches articles from a single RSS feed.

    Args:
        name: Human-readable name for this feed source.
        url: The RSS feed URL to fetch from.
        source_tier: Credibility tier (e.g. "primary", "expert", "major-outlet", "aggregator").
        credibility_weight: Multiplier for the composite score (0.0-1.0).
    """

    def __init__(
        self,
        name: str,
        url: str,
        source_tier: str = "general",
        credibility_weight: float = 1.0,
    ) -> None:
        super().__init__(fetcher_name=name)
        self._url = url
        self._source_tier = source_tier
        self._credibility_weight = credibility_weight

    @property
    def url(self) -> str:
        """The RSS feed URL."""
        return self._url

    def _fetch_impl(self) -> list[Article]:
        """Fetch and parse the RSS feed, filtering to last 3 days."""
        feed = feedparser.parse(self._url)

        if feed.bozo and not feed.entries:
            logger.warning(f"Failed to parse RSS feed '{self._name}': {feed.bozo_exception}")
            return []

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=3)

        articles: list[Article] = []
        for entry in feed.entries:
            article = _entry_to_article(
                entry,
                source_name=self._name,
                source_tier=self._source_tier,
                credibility_weight=self._credibility_weight,
            )
            if article and article.published_at >= cutoff_date:
                articles.append(article)

        logger.info(
            "RSS '%s': %d entries parsed, %d after 3-day filter",
            self._name, len(feed.entries), len(articles),
        )
        return articles
