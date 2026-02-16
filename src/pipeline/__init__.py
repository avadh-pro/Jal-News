"""Daily news pipeline — fetch, score, and deliver health news."""

import logging
import time

from src.fetcher import fetch_all_articles
from src.scorer import score_articles
from src.sender import send_whatsapp_message

logger = logging.getLogger(__name__)


def run_pipeline(dry_run: bool = False) -> bool:
    """Execute the full news pipeline: fetch → score → send.

    Args:
        dry_run: If True, print the WhatsApp message instead of sending it.

    Returns:
        True if the pipeline completed successfully, False otherwise.
    """
    start = time.time()
    logger.info("Pipeline started (dry_run=%s)", dry_run)

    # --- Stage 1: Fetch articles from all sources ---
    try:
        articles = fetch_all_articles()
        logger.info("Fetched %d articles", len(articles))
    except Exception as exc:
        logger.error("Fetch stage failed: %s", exc, exc_info=True)
        return False

    if not articles:
        logger.warning("No articles fetched — nothing to do")
        return False

    # --- Stage 2: Score and rank with AI ---
    try:
        top_articles = score_articles(articles, top_n=5)
        logger.info("Top %d articles selected", len(top_articles))
    except Exception as exc:
        logger.error("Scoring stage failed: %s", exc, exc_info=True)
        return False

    if not top_articles:
        logger.warning("Scoring returned no articles — skipping send")
        return False

    # --- Stage 3: Send to WhatsApp ---
    try:
        result = send_whatsapp_message(top_articles, dry_run=dry_run)
    except Exception as exc:
        logger.error("Send stage failed: %s", exc, exc_info=True)
        return False

    if not result.success:
        logger.error("WhatsApp delivery failed: %s", result.error)
        return False

    elapsed = time.time() - start
    logger.info(
        "Pipeline finished in %.1fs — %d fetched, %d scored, delivery=%s",
        elapsed,
        len(articles),
        len(top_articles),
        result.message_id or "ok",
    )
    return True
