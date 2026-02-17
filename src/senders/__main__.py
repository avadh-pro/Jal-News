"""Test script for the senders module (dry-run only).

Run with:
    python -m src.senders
"""

import logging
from datetime import datetime

from src.core.models import ScoredArticle
from src.formatters import TelegramFormatter
from src.senders import SenderFactory, TelegramSender

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Mock articles for testing
_MOCK_ARTICLES = [
    ScoredArticle(
        title="One in Three People Carry This Brain Parasite",
        description="A parasite hiding in your brain has a kill switch.",
        url="https://www.sciencedaily.com/releases/2026/02/260215-brain-parasite.htm",
        source_name="ScienceDaily",
        published_at=datetime.now(),
        score=9.2,
        summary="New UVA research reveals how immune cells fight back against a common brain parasite carried by one in three people worldwide.",
    ),
    ScoredArticle(
        title="Exercise May Be the Most Powerful Treatment for Depression",
        description="A sweeping review shows physical activity can ease depression.",
        url="https://www.medicalnewstoday.com/articles/exercise-depression-2026",
        source_name="Medical News Today",
        published_at=datetime.now(),
        score=8.8,
        summary="Running, swimming, and dancing can powerfully ease depression and anxiety, according to a sweeping new meta-analysis.",
    ),
    ScoredArticle(
        title="New Blood Test Detects 50 Types of Cancer Early",
        description="Galleri blood test shows promise in early cancer detection.",
        url="https://www.bbc.com/news/health-cancer-blood-test-2026",
        source_name="BBC Health",
        published_at=datetime.now(),
        score=8.5,
        summary="A simple blood test can now detect over 50 types of cancer before symptoms appear, potentially saving thousands of lives.",
    ),
]


if __name__ == "__main__":
    # Test 1: Direct TelegramSender construction
    print("=== Test 1: Direct TelegramSender (dry-run) ===\n")
    formatter = TelegramFormatter()
    sender = TelegramSender(
        bot_token="test-token",
        chat_id="test-chat-id",
        formatter=formatter,
    )
    result = sender.send(_MOCK_ARTICLES, dry_run=True)
    print(f"Result: success={result.success}, message_id={result.message_id}\n")

    # Test 2: SenderFactory
    print("=== Test 2: SenderFactory (dry-run) ===\n")
    sender2 = SenderFactory.create(
        "telegram",
        bot_token="test-token",
        chat_id="test-chat-id",
    )
    result2 = sender2.send(_MOCK_ARTICLES, dry_run=True)
    print(f"Result: success={result2.success}, message_id={result2.message_id}\n")

