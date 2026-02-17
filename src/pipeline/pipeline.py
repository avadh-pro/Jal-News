"""NewsPipeline — interface-driven pipeline for fetch → score → send."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from src.core.interfaces import IArticleFetcher, IArticleScorer, IMessageSender

if TYPE_CHECKING:
    from src.dedup.tracker import SentArticleTracker

logger = logging.getLogger(__name__)


class NewsPipeline:
    """Orchestrates the news curation pipeline.

    Depends only on abstract interfaces so that concrete implementations
    can be swapped via dependency injection.

    Args:
        fetcher: Component that fetches articles from external sources.
        scorer: Component that scores and ranks articles.
        sender: Component that sends the curated digest.
        dedup_tracker: Optional deduplication tracker. When provided,
            already-sent articles are filtered out before scoring and
            newly sent articles are recorded after delivery.
    """

    def __init__(
        self,
        fetcher: IArticleFetcher,
        scorer: IArticleScorer,
        sender: IMessageSender,
        dedup_tracker: SentArticleTracker | None = None,
    ) -> None:
        self._fetcher = fetcher
        self._scorer = scorer
        self._sender = sender
        self._dedup_tracker = dedup_tracker

    def run(self, top_n: int = 5, dry_run: bool = False) -> bool:
        """Execute the full pipeline: fetch → score → send.

        Args:
            top_n: Number of top-scoring articles to include.
            dry_run: If True, format and log but do not actually send.

        Returns:
            True if the pipeline completed successfully, False otherwise.
        """
        start = time.time()
        logger.info("Pipeline started (dry_run=%s)", dry_run)

        # --- Stage 1: Fetch articles ---
        try:
            articles = self._fetcher.fetch()
            logger.info("Fetched %d articles", len(articles))
        except Exception as exc:
            logger.error("Fetch stage failed: %s", exc, exc_info=True)
            return False

        if not articles:
            logger.warning("No articles fetched — nothing to do")
            return False

        # --- Stage 1.5: Deduplication (filter already-sent articles) ---
        if self._dedup_tracker is not None:
            articles = self._dedup_tracker.filter_unsent(articles)
            if not articles:
                logger.warning("All fetched articles already sent — nothing new")
                return False

        # --- Stage 2: Score and rank ---
        try:
            top_articles = self._scorer.score(articles, top_n=top_n)
            logger.info("Top %d articles selected", len(top_articles))
        except Exception as exc:
            logger.error("Scoring stage failed: %s", exc, exc_info=True)
            return False

        if not top_articles:
            logger.warning("Scoring returned no articles — skipping send")
            return False

        # --- Stage 3: Send digest ---
        try:
            result = self._sender.send(top_articles, dry_run=dry_run)
        except Exception as exc:
            logger.error("Send stage failed: %s", exc, exc_info=True)
            return False

        if not result.success:
            logger.error("Delivery failed: %s", result.error)
            return False

        # --- Stage 3.5: Mark sent articles for deduplication ---
        if self._dedup_tracker is not None and not dry_run:
            self._dedup_tracker.mark_sent([a.url for a in top_articles])

        elapsed = time.time() - start
        logger.info(
            "Pipeline completed in %.1fs (message_id=%s)",
            elapsed,
            result.message_id,
        )
        return True

