"""RSS feed fetcher implementing IArticleFetcher via BaseFetcher."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import feedparser
from dateutil import parser as dateutil_parser

from src.core.models import Article
from src.fetchers.base import BaseFetcher

logger = logging.getLogger(__name__)

# Default RSS feed sources (used by __main__.py for convenience)
RSS_FEEDS = [
    {"name": "ScienceDaily Health", "url": "https://www.sciencedaily.com/rss/health_medicine.xml"},
    {"name": "BBC Health", "url": "http://feeds.bbci.co.uk/news/health/rss.xml"},  # NEW - replaces Medical News Today
    {"name": "Medical Xpress", "url": "https://medicalxpress.com/rss-feed/"},
    {"name": "WHO News", "url": "https://www.who.int/rss-feeds/news-english.xml"},
    {"name": "STAT News", "url": "https://www.statnews.com/feed/"},  # NEW - replaces Healthline
    {"name": "ET HealthWorld", "url": "https://health.economictimes.indiatimes.com/rss/topstories"},
    {"name": "PhysioUpdate", "url": "https://www.physioupdate.co.uk/feed/"},
    {"name": "CDC Newsroom", "url": "https://tools.cdc.gov/podcasts/feed.asp?feedid=183"},  # NEW - additional source
    {"name": "Health Affairs", "url": "https://www.healthaffairs.org/action/showFeed?type=etoc&feed=rss&jc=hlthaff"},  # NEW - additional source
]


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


def _entry_to_article(entry: dict, source_name: str) -> Optional[Article]:
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
    )


class RSSFetcher(BaseFetcher):
    """Fetches articles from a single RSS feed.

    Args:
        name: Human-readable name for this feed source.
        url: The RSS feed URL to fetch from.
    """

    def __init__(self, name: str, url: str) -> None:
        super().__init__(fetcher_name=name)
        self._url = url

    @property
    def url(self) -> str:
        """The RSS feed URL."""
        return self._url

    def _fetch_impl(self) -> list[Article]:
        """Fetch and parse the RSS feed."""
        feed = feedparser.parse(self._url)

        if feed.bozo and not feed.entries:
            logger.warning(f"Failed to parse RSS feed '{self._name}': {feed.bozo_exception}")
            return []

        articles: list[Article] = []
        for entry in feed.entries:
            article = _entry_to_article(entry, source_name=self._name)
            if article:
                articles.append(article)

        return articles

