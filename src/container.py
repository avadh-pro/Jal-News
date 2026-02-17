"""Dependency injection container — wires concrete implementations together."""

from __future__ import annotations

import logging

from src.config.config import Settings, settings as _default_settings
from src.fetchers.composite import CompositeFetcher
from src.fetchers.newsapi_fetcher import NewsAPIFetcher
from src.fetchers.rss_fetcher import RSSFetcher
from src.formatters.telegram_formatter import TelegramFormatter
from src.pipeline.pipeline import NewsPipeline
from src.scorers.claude_scorer import ClaudeScorer
from src.senders.telegram_sender import TelegramSender

logger = logging.getLogger(__name__)

# RSS feed sources used by the pipeline
RSS_FEEDS = [
    {"name": "ScienceDaily Health", "url": "https://www.sciencedaily.com/rss/health_medicine.xml"},
    {"name": "Medical News Today", "url": "https://www.medicalnewstoday.com/rss"},
    {"name": "Medical Xpress", "url": "https://medicalxpress.com/rss-feed/"},
    {"name": "WHO News", "url": "https://www.who.int/rss-feeds/news-english.xml"},
    {"name": "Healthline", "url": "https://www.healthline.com/rss"},
    {"name": "ET HealthWorld", "url": "https://health.economictimes.indiatimes.com/rss/topstories"},
    {"name": "PhysioUpdate", "url": "https://www.physioupdate.co.uk/feed/"},
]


def create_pipeline(settings: Settings | None = None) -> NewsPipeline:
    """Create a fully configured :class:`NewsPipeline` from settings.

    Wires together concrete implementations:
    - RSS + NewsAPI fetchers wrapped in a CompositeFetcher
    - ClaudeScorer for AI-powered article ranking
    - TelegramSender with TelegramFormatter for delivery

    Args:
        settings: Application settings. Falls back to the global singleton
            from ``src.config`` when *None*.

    Returns:
        A ready-to-run NewsPipeline instance.
    """
    if settings is None:
        settings = _default_settings

    # --- Fetchers ---
    fetchers = [RSSFetcher(name=feed["name"], url=feed["url"]) for feed in RSS_FEEDS]

    if settings.newsapi_key:
        fetchers.append(NewsAPIFetcher(api_key=settings.newsapi_key))
    else:
        logger.warning("NEWSAPI_KEY not set — skipping NewsAPI fetcher")

    composite_fetcher = CompositeFetcher(fetchers=fetchers)

    # --- Scorer ---
    scorer = ClaudeScorer(api_key=settings.anthropic_api_key)

    # --- Sender ---
    formatter = TelegramFormatter()
    sender = TelegramSender(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
        formatter=formatter,
    )

    return NewsPipeline(
        fetcher=composite_fetcher,
        scorer=scorer,
        sender=sender,
    )

