"""Abstract interface for message formatting."""

from abc import ABC, abstractmethod

from src.core.models import ScoredArticle


class IMessageFormatter(ABC):
    """Interface for components that format scored articles into messages."""

    @abstractmethod
    def format(self, articles: list[ScoredArticle]) -> str:
        """Format scored articles into a message string.

        Args:
            articles: Scored articles to format.

        Returns:
            Formatted message string ready for sending.
        """
        ...

