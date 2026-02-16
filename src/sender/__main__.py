"""Test script for the WhatsApp sender module.

Run with:
    python -m src.sender
"""

import logging
from datetime import datetime

from src.models import ScoredArticle
from src.sender import send_whatsapp_message

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
    ScoredArticle(
        title="Gut Bacteria May Hold the Key to Treating Autoimmune Diseases",
        description="Researchers find gut microbiome link to autoimmune conditions.",
        url="https://www.medicalxpress.com/news/2026-02-gut-bacteria-autoimmune.html",
        source_name="Medical Xpress",
        published_at=datetime.now(),
        score=8.1,
        summary="Scientists discover specific gut bacteria strains that could revolutionize treatment for rheumatoid arthritis and lupus.",
    ),
    ScoredArticle(
        title="WHO Warns of Rising Antibiotic Resistance in South Asia",
        description="WHO report highlights growing threat of superbugs.",
        url="https://www.who.int/news/item/2026-02-antibiotic-resistance",
        source_name="WHO",
        published_at=datetime.now(),
        score=7.6,
        summary="A new WHO report warns that antibiotic resistance in South Asia is accelerating, urging immediate action on prescription practices.",
    ),
]


if __name__ == "__main__":
    print("Testing WhatsApp sender in dry-run mode...\n")
    result = send_whatsapp_message(_MOCK_ARTICLES, dry_run=True)
    print(f"\nResult: success={result.success}, message_id={result.message_id}")

