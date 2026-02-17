"""Abstract interface for article scoring."""

from abc import ABC, abstractmethod

from src.core.models import Article, ScoredArticle


class IArticleScorer(ABC):
    """Interface for components that score and rank articles."""

    @abstractmethod
    def score(self, articles: list[Article], top_n: int = 5) -> list[ScoredArticle]:
        """Score and rank articles, returning the top N.

        Args:
            articles: List of articles to score.
            top_n: Number of top-scoring articles to return.

        Returns:
            Top N ScoredArticle objects sorted by score (highest first).
        """
        ...

