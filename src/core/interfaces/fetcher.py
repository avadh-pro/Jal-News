"""Abstract interface for article fetching."""

from abc import ABC, abstractmethod

from src.core.models import Article


class IArticleFetcher(ABC):
    """Interface for components that fetch articles from external sources."""

    @abstractmethod
    def fetch(self) -> list[Article]:
        """Fetch articles from the source.

        Returns:
            List of Article objects retrieved from the source.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this fetcher (e.g. 'NewsAPI', 'RSS')."""
        ...

