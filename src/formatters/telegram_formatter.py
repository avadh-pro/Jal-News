"""Telegram-specific message formatter using Markdown."""

from datetime import datetime

from src.core.models import ScoredArticle
from src.formatters.base import BaseFormatter

# Number emojis for article ranking
_NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

# Category emojis to rotate through for visual variety
_CATEGORY_EMOJIS = ["🧬", "🧠", "💊", "🏥", "🔬", "💪", "🩺", "🫀", "🦠", "🧪"]


class TelegramFormatter(BaseFormatter):
    """Format scored articles into a Telegram Markdown message."""

    def _format_header(self) -> str:
        """Build the message header with date and branding."""
        today = datetime.now().strftime("%B %d, %Y")
        return (
            "🏥 *Amaro Labs Health Digest*\n"
            f"📅 {today}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

    def _format_article(self, article: ScoredArticle, index: int) -> str:
        """Format a single article entry with Telegram Markdown."""
        number = _NUMBER_EMOJIS[index] if index < len(_NUMBER_EMOJIS) else f"{index + 1}."
        emoji = _CATEGORY_EMOJIS[index % len(_CATEGORY_EMOJIS)]

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
        return (
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✨ _Curated by AI for Amaro Labs_\n"
            "_Reply STOP to unsubscribe_"
        )

