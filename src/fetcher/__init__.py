"""News fetcher module — aggregates health news from RSS feeds and NewsAPI."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from typing import List

from src.models import Article

from .newsapi_fetcher import fetch_newsapi
from .rss_fetcher import RSS_FEEDS, fetch_rss_feed

logger = logging.getLogger(__name__)


def _normalize_title(title: str) -> str:
    """Normalize a title for deduplication comparison."""
    return title.lower().strip()


def _is_duplicate(article: Article, seen: List[Article], threshold: float = 0.85) -> bool:
    """Check if an article is a duplicate based on URL or title similarity."""
    norm_title = _normalize_title(article.title)
    for existing in seen:
        # Exact URL match
        if article.url == existing.url:
            return True
        # Title similarity check
        existing_norm = _normalize_title(existing.title)
        if SequenceMatcher(None, norm_title, existing_norm).ratio() >= threshold:
            return True
    return False


def _filter_recent(articles: List[Article], hours: int = 24) -> List[Article]:
    """Filter articles to only those published within the last N hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = []
    for article in articles:
        pub = article.published_at
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        if pub >= cutoff:
            recent.append(article)
    return recent


def _deduplicate(articles: List[Article]) -> List[Article]:
    """Remove duplicate articles based on URL and title similarity."""
    unique: List[Article] = []
    for article in articles:
        if not _is_duplicate(article, unique):
            unique.append(article)
    return unique


def fetch_all_articles(hours: int = 24) -> List[Article]:
    """Fetch articles from all sources in parallel, deduplicate, and filter.

    Args:
        hours: Only return articles from the last N hours (default: 24).

    Returns:
        Deduplicated list of Article objects sorted by published_at (newest first).
    """
    all_articles: List[Article] = []
    errors: List[str] = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}

        # Submit RSS feed tasks
        for feed in RSS_FEEDS:
            future = executor.submit(fetch_rss_feed, feed["name"], feed["url"])
            futures[future] = feed["name"]

        # Submit NewsAPI task
        newsapi_future = executor.submit(fetch_newsapi)
        futures[newsapi_future] = "NewsAPI"

        # Collect results
        for future in as_completed(futures):
            source_name = futures[future]
            try:
                articles = future.result(timeout=60)
                all_articles.extend(articles)
                logger.info(f"✓ {source_name}: {len(articles)} articles")
            except Exception as e:
                errors.append(f"{source_name}: {e}")
                logger.error(f"✗ {source_name} failed: {e}")

    if errors:
        logger.warning(f"{len(errors)} source(s) failed: {', '.join(errors)}")

    # Filter to recent articles only
    recent = _filter_recent(all_articles, hours=hours)
    logger.info(f"Filtered to {len(recent)} articles from last {hours} hours (from {len(all_articles)} total)")

    # Deduplicate
    unique = _deduplicate(recent)
    logger.info(f"After deduplication: {len(unique)} unique articles")

    # Sort by published date (newest first)
    unique.sort(key=lambda a: a.published_at, reverse=True)

    return unique
