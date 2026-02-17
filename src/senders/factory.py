"""Sender factory — create senders by type string."""

from src.core.interfaces import IMessageFormatter, IMessageSender
from src.formatters import TelegramFormatter
from src.senders.telegram_sender import TelegramSender


class SenderFactory:
    """Factory for creating message senders by platform type."""

    @staticmethod
    def create(sender_type: str, **kwargs: object) -> IMessageSender:
        """Create a sender instance by type.

        Args:
            sender_type: Platform identifier (e.g. ``"telegram"``).
            **kwargs: Platform-specific arguments forwarded to the sender
                constructor. For ``"telegram"``: ``bot_token``, ``chat_id``,
                and optionally ``formatter`` and ``max_retries``.

        Returns:
            An IMessageSender implementation.

        Raises:
            ValueError: If ``sender_type`` is not supported.
        """
        if sender_type == "telegram":
            bot_token = kwargs.get("bot_token")
            chat_id = kwargs.get("chat_id")
            if not bot_token or not chat_id:
                raise ValueError(
                    "TelegramSender requires 'bot_token' and 'chat_id'"
                )
            formatter = kwargs.get("formatter")
            if formatter is None:
                formatter = TelegramFormatter()
            if not isinstance(formatter, IMessageFormatter):
                raise TypeError("formatter must implement IMessageFormatter")
            max_retries = kwargs.get("max_retries", 2)
            return TelegramSender(
                bot_token=str(bot_token),
                chat_id=str(chat_id),
                formatter=formatter,
                max_retries=int(max_retries),  # type: ignore[arg-type]
            )

        raise ValueError(f"Unsupported sender type: {sender_type!r}")

