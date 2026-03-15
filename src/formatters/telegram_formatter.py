"""Telegram-specific message formatter using Markdown."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from src.core.models import ScoredArticle
from src.formatters.base import BaseFormatter

if TYPE_CHECKING:
    from src.channels.channel import Channel

# Number emojis for article ranking
_NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

# Default category emojis (used when no channel is provided)
_DEFAULT_CATEGORY_EMOJIS = ["📰", "🔍", "💡", "⚡", "🌐"]


class TelegramFormatter(BaseFormatter):
    """Format scored articles into a Telegram Markdown message.

    Args:
        channel: Optional channel config for custom branding. When None,
            uses generic defaults.
    """

    def __init__(self, channel: Channel | None = None) -> None:
        self._channel = channel

    def _format_header(self) -> str:
        """Build the message header with date and branding."""
        today = datetime.now().strftime("%B %d, %Y")

        if self._channel:
            emoji = self._channel.header_emoji
            title = self._channel.name
        else:
            emoji = "📰"
            title = "News Digest"

        return (
            f"{emoji} *{title}*\n"
            f"📅 {today}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

    def _format_article(self, article: ScoredArticle, index: int) -> str:
        """Format a single article entry with Telegram Markdown."""
        number = _NUMBER_EMOJIS[index] if index < len(_NUMBER_EMOJIS) else f"{index + 1}."

        if self._channel:
            emojis = self._channel.category_emojis
        else:
            emojis = _DEFAULT_CATEGORY_EMOJIS

        emoji = emojis[index % len(emojis)] if emojis else "📰"

        # Use the AI-generated summary if available, otherwise fall back to description
        summary = article.summary or article.description
        # Truncate long summaries to keep the message compact
        if len(summary) > 150:
            summary = summary[:147] + "..."

        return (
            f"\n{number} {emoji} *{article.title}*\n"
            f"{summary}\n"
            f"📰 {article.source_name}\n"
            f"🔗 {article.url}"
        )

    def _format_footer(self) -> str:
        """Build the message footer."""
        if self._channel:
            footer = self._channel.footer_text
        else:
            footer = "Curated by AI"

        return (
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ _{footer}_\n"
            "_Reply STOP to unsubscribe_"
        )
