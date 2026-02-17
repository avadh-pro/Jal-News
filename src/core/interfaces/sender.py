"""Abstract interface for message sending."""

from abc import ABC, abstractmethod

from src.core.models import ScoredArticle
from src.core.result import SendResult


class IMessageSender(ABC):
    """Interface for components that send curated articles to a channel."""

    @abstractmethod
    def send(self, articles: list[ScoredArticle], dry_run: bool = False) -> SendResult:
        """Send formatted articles to the target channel.

        Args:
            articles: Scored articles to send.
            dry_run: If True, format and log but do not actually send.

        Returns:
            SendResult indicating success/failure with message ID or error.
        """
        ...

