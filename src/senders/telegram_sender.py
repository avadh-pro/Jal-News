"""Telegram sender using the Bot API."""

import logging

import requests

from src.core.interfaces import IMessageFormatter
from src.core.result import SendResult
from src.senders.base import BaseSender

logger = logging.getLogger(__name__)

_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramSender(BaseSender):
    """Send messages via the Telegram Bot API.

    Uses composition: receives an ``IMessageFormatter`` for message formatting
    and ``bot_token`` / ``chat_id`` for Telegram authentication.
    """

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        formatter: IMessageFormatter,
        max_retries: int = 2,
    ) -> None:
        super().__init__(formatter=formatter, max_retries=max_retries)
        self._bot_token = bot_token
        self._chat_id = chat_id

    def _send_impl(self, message: str) -> SendResult:
        """Send a message via the Telegram Bot API.

        Args:
            message: The formatted message string to send.

        Returns:
            SendResult indicating success/failure.
        """
        url = _API_URL.format(token=self._bot_token)
        payload = {
            "chat_id": self._chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }

        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                msg_id = str(data.get("result", {}).get("message_id", "unknown"))
                logger.info("Telegram message sent successfully (id=%s)", msg_id)
                return SendResult(success=True, message_id=msg_id)

            error = f"HTTP {resp.status_code}: {resp.text}"
            logger.warning("Telegram API error: %s", error)
            return SendResult(success=False, error=error)
        except requests.RequestException as exc:
            error = str(exc)
            logger.warning("Telegram request failed: %s", error)
            return SendResult(success=False, error=error)

