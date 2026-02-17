"""Base fetcher with common logging and error handling."""

from __future__ import annotations

import logging
from abc import abstractmethod

from src.core.interfaces import IArticleFetcher
from src.core.models import Article

logger = logging.getLogger(__name__)


class BaseFetcher(IArticleFetcher):
    """Abstract base class for article fetchers.

    Provides common error handling and logging around the fetch operation.
    Subclasses implement ``_fetch_impl()`` with source-specific logic.
    """

    def __init__(self, fetcher_name: str) -> None:
        self._name = fetcher_name

    @property
    def name(self) -> str:
        """Human-readable name of this fetcher."""
        return self._name

    @abstractmethod
    def _fetch_impl(self) -> list[Article]:
        """Fetch articles from the source (implemented by subclasses).

        Returns:
            List of Article objects retrieved from the source.
        """
        ...

    def fetch(self) -> list[Article]:
        """Fetch articles with error handling and logging.

        Calls ``_fetch_impl()`` and wraps it in try/except so that a
        single fetcher failure never crashes the whole pipeline.
        """
        logger.info(f"Fetching articles from {self._name}")
        try:
            articles = self._fetch_impl()
            logger.info(f"Fetched {len(articles)} articles from {self._name}")
            return articles
        except Exception as e:
            logger.error(f"Error fetching from {self._name}: {e}")
            return []

