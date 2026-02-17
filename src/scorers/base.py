"""Base scorer with common batch-processing logic."""

import logging
from abc import abstractmethod

from src.core.interfaces import IArticleScorer
from src.core.models import Article, ScoredArticle

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 10


class BaseScorer(IArticleScorer):
    """Abstract base scorer that handles batching and result assembly.

    Subclasses implement ``_score_batch`` to call a specific AI provider.

    Args:
        batch_size: Number of articles per API call (default: 10).
    """

    def __init__(self, batch_size: int = DEFAULT_BATCH_SIZE) -> None:
        self.batch_size = batch_size

    # ------------------------------------------------------------------
    # Abstract hook — subclasses must implement
    # ------------------------------------------------------------------

    @abstractmethod
    def _score_batch(
        self,
        articles: list[Article],
        start_index: int,
    ) -> list[dict]:
        """Score a single batch of articles.

        Args:
            articles: The batch of Article objects to score.
            start_index: The global index offset for this batch.

        Returns:
            List of score dicts with keys: index, shareability, novelty,
            relevance, viral_potential, summary.
        """
        ...

    # ------------------------------------------------------------------
    # Public API (implements IArticleScorer)
    # ------------------------------------------------------------------

    def score(
        self,
        articles: list[Article],
        top_n: int = 5,
    ) -> list[ScoredArticle]:
        """Score and rank articles, returning the top N.

        Articles are sent in batches to minimize API calls. Each article
        receives scores for shareability, novelty, relevance, and viral
        potential (1-10). A composite score (average of the four) is
        calculated for ranking.

        Args:
            articles: List of Article objects to score.
            top_n: Number of top-scoring articles to return.

        Returns:
            Top N ScoredArticle objects sorted by composite score (highest first).
        """
        if not articles:
            logger.warning("No articles to score")
            return []

        # Collect all score dicts across batches
        all_scores: list[dict] = []

        for batch_start in range(0, len(articles), self.batch_size):
            batch = articles[batch_start : batch_start + self.batch_size]
            logger.info(
                f"Scoring batch {batch_start // self.batch_size + 1} "
                f"({len(batch)} articles, index {batch_start}-"
                f"{batch_start + len(batch) - 1})"
            )
            scores = self._score_batch(batch, batch_start)
            all_scores.extend(scores)

        # Map scores by index for lookup
        score_map: dict[int, dict] = {}
        for s in all_scores:
            idx = s.get("index")
            if idx is not None:
                score_map[int(idx)] = s

        # Build ScoredArticle list
        scored: list[ScoredArticle] = []
        for i, article in enumerate(articles):
            s = score_map.get(i)
            if s is None:
                logger.warning(
                    f"No score returned for article {i}: {article.title[:60]}"
                )
                scored.append(
                    ScoredArticle(
                        title=article.title,
                        description=article.description,
                        url=article.url,
                        source_name=article.source_name,
                        published_at=article.published_at,
                        image_url=article.image_url,
                        score=0.0,
                        summary="",
                    )
                )
                continue

            composite = (
                s.get("shareability", 0)
                + s.get("novelty", 0)
                + s.get("relevance", 0)
                + s.get("viral_potential", 0)
            ) / 4.0

            scored.append(
                ScoredArticle(
                    title=article.title,
                    description=article.description,
                    url=article.url,
                    source_name=article.source_name,
                    published_at=article.published_at,
                    image_url=article.image_url,
                    score=round(composite, 2),
                    summary=s.get("summary", ""),
                )
            )

        # Sort by score descending and return top N
        scored.sort(key=lambda a: a.score, reverse=True)
        return scored[:top_n]

