"""Core data models for the news curation pipeline.

Provides Article and ScoredArticle dataclasses with proper inheritance
(ScoredArticle extends Article) to satisfy the Liskov Substitution Principle.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """Represents a fetched news article."""

    title: str
    description: str
    url: str
    source_name: str
    published_at: datetime
    image_url: Optional[str] = None
    source_tier: str = "general"
    credibility_weight: float = 1.0
    coverage_count: int = 1

    def __hash__(self) -> int:
        return hash(self.url)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Article):
            return NotImplemented
        return self.url == other.url


@dataclass
class ScoredArticle(Article):
    """An article that has been scored and summarized by AI.

    Inherits all fields from Article and adds score and summary.
    """

    score: float = 0.0
    summary: str = ""

    @classmethod
    def from_article(
        cls, article: Article, score: float = 0.0, summary: str = ""
    ) -> "ScoredArticle":
        """Create a ScoredArticle from an Article with score and summary."""
        return cls(
            title=article.title,
            description=article.description,
            url=article.url,
            source_name=article.source_name,
            published_at=article.published_at,
            image_url=article.image_url,
            source_tier=article.source_tier,
            credibility_weight=article.credibility_weight,
            coverage_count=article.coverage_count,
            score=score,
            summary=summary,
        )
