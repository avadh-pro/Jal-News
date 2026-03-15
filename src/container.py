"""Dependency injection container — wires concrete implementations together."""

from __future__ import annotations

import logging

from src.channels.channel import Channel
from src.channels.loader import load_channel
from src.config.config import Settings, settings as _default_settings
from src.dedup.tracker import SentArticleTracker, storage_path_for_channel
from src.fetchers.composite import CompositeFetcher
from src.fetchers.newsapi_fetcher import NewsAPIFetcher
from src.fetchers.rss_fetcher import RSSFetcher
from src.formatters.telegram_formatter import TelegramFormatter
from src.pipeline.pipeline import NewsPipeline
from src.scorers.claude_scorer import ClaudeScorer
from src.senders.telegram_sender import TelegramSender

logger = logging.getLogger(__name__)

# Legacy RSS feeds — used only when no channel is specified (backwards compat)
_LEGACY_RSS_FEEDS = [
    {"name": "ScienceDaily Health", "url": "https://www.sciencedaily.com/rss/health_medicine.xml"},
    {"name": "BBC Health", "url": "http://feeds.bbci.co.uk/news/health/rss.xml"},
    {"name": "Medical Xpress", "url": "https://medicalxpress.com/rss-feed/"},
    {"name": "WHO News", "url": "https://www.who.int/rss-feeds/news-english.xml"},
    {"name": "STAT News", "url": "https://www.statnews.com/feed/"},
    {"name": "ET HealthWorld", "url": "https://health.economictimes.indiatimes.com/rss/topstories"},
    {"name": "PhysioUpdate", "url": "https://www.physioupdate.co.uk/feed/"},
    {"name": "CDC Newsroom", "url": "https://tools.cdc.gov/podcasts/feed.asp?feedid=183"},
    {"name": "Health Affairs", "url": "https://www.healthaffairs.org/action/showFeed?type=etoc&feed=rss&jc=hlthaff"},
]


def create_pipeline(
    settings: Settings | None = None,
    channel: Channel | None = None,
    channel_slug: str | None = None,
) -> NewsPipeline:
    """Create a fully configured :class:`NewsPipeline`.

    Can be called three ways:
    1. ``create_pipeline()`` — legacy mode, uses hardcoded health feeds.
    2. ``create_pipeline(channel=my_channel)`` — pass a Channel object directly.
    3. ``create_pipeline(channel_slug="ai-video")`` — load channel from YAML by slug.
    """
    if settings is None:
        settings = _default_settings

    # Resolve channel from slug if provided
    if channel is None and channel_slug:
        channel = load_channel(channel_slug)
        logger.info("Loaded channel: %s (%s)", channel.name, channel.slug)

    # --- Fetchers ---
    if channel and channel.feeds:
        feeds = channel.feeds
    else:
        feeds = _LEGACY_RSS_FEEDS

    fetchers = [
        RSSFetcher(
            name=feed["name"],
            url=feed["url"],
            source_tier=feed.get("tier", "general"),
            credibility_weight=float(feed.get("weight", 1.0)),
        )
        for feed in feeds
    ]

    if settings.newsapi_key:
        query = channel.newsapi_query if channel else ""
        domains = channel.newsapi_domains if channel else ""
        fetchers.append(NewsAPIFetcher(
            api_key=settings.newsapi_key,
            query=query,
            domains=domains,
        ))
    else:
        logger.warning("NEWSAPI_KEY not set — skipping NewsAPI fetcher")

    composite_fetcher = CompositeFetcher(fetchers=fetchers)

    # --- Scorer ---
    scorer = ClaudeScorer(
        api_key=settings.anthropic_api_key,
        channel=channel,
    )

    # --- Sender ---
    formatter = TelegramFormatter(channel=channel)
    chat_id = (channel.telegram_chat_id if channel else "") or settings.telegram_chat_id

    sender = TelegramSender(
        bot_token=settings.telegram_bot_token,
        chat_id=chat_id,
        formatter=formatter,
    )

    # --- Deduplication ---
    dedup_tracker = None
    if settings.enable_dedup:
        slug = channel.slug if channel else None
        dedup_tracker = SentArticleTracker(
            storage_path=storage_path_for_channel(slug)
        )
        logger.info("Deduplication enabled — tracking sent articles")
    else:
        logger.info("Deduplication disabled (ENABLE_DEDUP != true)")

    return NewsPipeline(
        fetcher=composite_fetcher,
        scorer=scorer,
        sender=sender,
        dedup_tracker=dedup_tracker,
    )
