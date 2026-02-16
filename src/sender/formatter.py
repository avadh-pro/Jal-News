"""Format curated articles into a WhatsApp-friendly message."""

from datetime import datetime

from src.models import ScoredArticle

# WhatsApp text message character limit
_MAX_LENGTH = 4096

# Number emojis for article ranking
_NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

# Category emojis to rotate through for visual variety
_CATEGORY_EMOJIS = ["🧬", "🧠", "💊", "🏥", "🔬", "💪", "🩺", "🫀", "🦠", "🧪"]


def _format_header() -> str:
    """Build the message header with date and branding."""
    today = datetime.now().strftime("%B %d, %Y")
    return (
        "🏥 *Amaro Labs Health Digest*\n"
        f"📅 {today}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def _format_article(article: ScoredArticle, index: int) -> str:
    """Format a single article entry."""
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


def _format_footer() -> str:
    """Build the message footer."""
    return (
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ _Curated by AI for Amaro Labs_\n"
        "_Reply STOP to unsubscribe_"
    )


def format_digest(articles: list[ScoredArticle]) -> str:
    """Format a list of scored articles into a WhatsApp message.

    Builds the message incrementally and stops adding articles if the
    4096-character WhatsApp limit would be exceeded.

    Args:
        articles: Scored and ranked articles (best first).

    Returns:
        A formatted plain-text message ready for WhatsApp delivery.
    """
    header = _format_header()
    footer = _format_footer()

    # Reserve space for header + footer + some padding
    reserved = len(header) + len(footer) + 10
    remaining = _MAX_LENGTH - reserved

    body_parts: list[str] = []
    for i, article in enumerate(articles):
        part = _format_article(article, i)
        if len(part) > remaining:
            break
        body_parts.append(part)
        remaining -= len(part)

    body = "".join(body_parts)
    return f"{header}\n{body}\n{footer}"

