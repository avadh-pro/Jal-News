"""Base formatter with template method pattern."""

from abc import abstractmethod

from src.core.interfaces import IMessageFormatter
from src.core.models import ScoredArticle

# Telegram message character limit
_MAX_LENGTH = 4096


class BaseFormatter(IMessageFormatter):
    """Base formatter that combines header, articles, and footer.

    Subclasses implement the three abstract methods to define
    platform-specific formatting. The ``format()`` method assembles
    them and respects the message length limit.
    """

    max_length: int = _MAX_LENGTH

    @abstractmethod
    def _format_header(self) -> str:
        """Build the message header."""
        ...

    @abstractmethod
    def _format_article(self, article: ScoredArticle, index: int) -> str:
        """Format a single article entry."""
        ...

    @abstractmethod
    def _format_footer(self) -> str:
        """Build the message footer."""
        ...

    def format(self, articles: list[ScoredArticle]) -> str:
        """Format scored articles into a message string.

        Builds the message incrementally and stops adding articles
        if the character limit would be exceeded.

        Args:
            articles: Scored articles to format.

        Returns:
            Formatted message string ready for sending.
        """
        header = self._format_header()
        footer = self._format_footer()

        # Reserve space for header + footer + padding
        reserved = len(header) + len(footer) + 10
        remaining = self.max_length - reserved

        body_parts: list[str] = []
        for i, article in enumerate(articles):
            part = self._format_article(article, i)
            if len(part) > remaining:
                break
            body_parts.append(part)
            remaining -= len(part)

        body = "".join(body_parts)
        return f"{header}\n{body}\n{footer}"

