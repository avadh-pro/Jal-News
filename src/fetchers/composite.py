"""Composite fetcher that aggregates multiple fetchers with deduplication."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher

from src.core.interfaces import IArticleFetcher
from src.core.models import Article

logger = logging.getLogger(__name__)


def _normalize_title(title: str) -> str:
    """Normalize a title for deduplication comparison."""
    return title.lower().strip()


def _is_duplicate(
    article: Article, seen: list[Article], threshold: float = 0.85
) -> bool:
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


def _deduplicate(articles: list[Article]) -> list[Article]:
    """Remove duplicate articles based on URL and title similarity."""
    unique: list[Article] = []
    for article in articles:
        if not _is_duplicate(article, unique):
            unique.append(article)
    return unique


class CompositeFetcher(IArticleFetcher):
    """Aggregates multiple fetchers, runs them in parallel, and deduplicates.

    Args:
        fetchers: List of IArticleFetcher instances to aggregate.
        max_workers: Maximum number of parallel threads (default: 8).
    """

    def __init__(
        self,
        fetchers: list[IArticleFetcher],
        max_workers: int = 8,
    ) -> None:
        self._fetchers = fetchers
        self._max_workers = max_workers

    @property
    def name(self) -> str:
        """Human-readable name of this composite fetcher."""
        return "CompositeFetcher"

    def fetch(self) -> list[Article]:
        """Fetch articles from all child fetchers in parallel and deduplicate.

        Each fetcher runs in its own thread. Failures in individual fetchers
        are logged but do not prevent other fetchers from completing.
        """
        all_articles: list[Article] = []
        errors: list[str] = []

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = {}
            for fetcher in self._fetchers:
                future = executor.submit(fetcher.fetch)
                futures[future] = fetcher.name

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
            logger.warning(
                f"{len(errors)} source(s) failed: {', '.join(errors)}"
            )

        # Deduplicate
        unique = _deduplicate(all_articles)
        logger.info(
            f"CompositeFetcher: {len(unique)} unique articles "
            f"(from {len(all_articles)} total)"
        )

        # Sort by published date (newest first)
        unique.sort(key=lambda a: a.published_at, reverse=True)

        return unique

