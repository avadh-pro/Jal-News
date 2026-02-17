"""Base sender with retry logic."""

import logging
from abc import abstractmethod

from src.core.interfaces import IMessageFormatter, IMessageSender
from src.core.models import ScoredArticle
from src.core.result import SendResult

logger = logging.getLogger(__name__)

_DEFAULT_MAX_RETRIES = 2


class BaseSender(IMessageSender):
    """Base sender that formats messages and retries on failure.

    Subclasses implement ``_send_impl()`` for platform-specific delivery.
    The ``send()`` method handles formatting, dry-run mode, and retry logic.
    """

    def __init__(
        self,
        formatter: IMessageFormatter,
        max_retries: int = _DEFAULT_MAX_RETRIES,
    ) -> None:
        self._formatter = formatter
        self._max_retries = max_retries

    @abstractmethod
    def _send_impl(self, message: str) -> SendResult:
        """Send a formatted message to the target platform.

        Args:
            message: The formatted message string to send.

        Returns:
            SendResult indicating success/failure.
        """
        ...

    def send(self, articles: list[ScoredArticle], dry_run: bool = False) -> SendResult:
        """Format and send articles with retry logic.

        Args:
            articles: Scored articles to send.
            dry_run: If True, format and log but do not actually send.

        Returns:
            SendResult indicating success/failure with message ID or error.
        """
        if not articles:
            logger.warning("No articles to send")
            return SendResult(success=False, error="No articles provided")

        message = self._formatter.format(articles)
        logger.info("Formatted digest (%d chars, %d articles)", len(message), len(articles))

        if dry_run:
            print("\n" + "=" * 50)
            print("DRY RUN — message preview:")
            print("=" * 50)
            print(message)
            print("=" * 50 + "\n")
            return SendResult(success=True, message_id="dry-run")

        last_error = ""
        for attempt in range(1, self._max_retries + 1):
            result = self._send_impl(message)
            if result.success:
                return result
            last_error = result.error or "Unknown error"
            logger.warning(
                "Send failed (attempt %d/%d): %s",
                attempt,
                self._max_retries,
                last_error,
            )

        logger.error(
            "Delivery failed after %d attempts: %s",
            self._max_retries,
            last_error,
        )
        return SendResult(success=False, error=last_error)

