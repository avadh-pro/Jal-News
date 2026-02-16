"""RSS feed fetcher for health news sources."""

import logging
from datetime import datetime, timezone
from typing import List, Optional

import feedparser
from dateutil import parser as dateutil_parser

from src.models import Article

logger = logging.getLogger(__name__)

# RSS feed sources configuration
RSS_FEEDS = [
    {"name": "ScienceDaily Health", "url": "https://www.sciencedaily.com/rss/health_medicine.xml"},
    {"name": "Medical News Today", "url": "https://www.medicalnewstoday.com/rss"},
    {"name": "Medical Xpress", "url": "https://medicalxpress.com/rss-feed/"},
    {"name": "WHO News", "url": "https://www.who.int/rss-feeds/news-english.xml"},
    {"name": "Healthline", "url": "https://www.healthline.com/rss"},
    {"name": "ET HealthWorld", "url": "https://health.economictimes.indiatimes.com/rss/topstories"},
    {"name": "PhysioUpdate", "url": "https://www.physioupdate.co.uk/feed/"},
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
        # Default to now if no date found — will be filtered later
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


def fetch_rss_feed(name: str, url: str) -> List[Article]:
    """Fetch and parse a single RSS feed. Returns list of Articles."""
    logger.info(f"Fetching RSS feed: {name} ({url})")
    try:
        feed = feedparser.parse(url)

        if feed.bozo and not feed.entries:
            logger.warning(f"Failed to parse RSS feed '{name}': {feed.bozo_exception}")
            return []

        articles = []
        for entry in feed.entries:
            article = _entry_to_article(entry, source_name=name)
            if article:
                articles.append(article)

        logger.info(f"Fetched {len(articles)} articles from {name}")
        return articles

    except Exception as e:
        logger.error(f"Error fetching RSS feed '{name}': {e}")
        return []


def fetch_all_rss() -> List[Article]:
    """Fetch articles from all configured RSS feeds sequentially."""
    all_articles: List[Article] = []
    for feed_config in RSS_FEEDS:
        articles = fetch_rss_feed(feed_config["name"], feed_config["url"])
        all_articles.extend(articles)
    return all_articles

