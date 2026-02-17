"""Core module — interfaces, models, and result types for the news curation pipeline."""

from src.core.interfaces import (
    IArticleFetcher,
    IArticleScorer,
    IMessageFormatter,
    IMessageSender,
)
from src.core.models import Article, ScoredArticle
from src.core.result import FetchResult, ScoreResult, SendResult

__all__ = [
    # Models
    "Article",
    "ScoredArticle",
    # Interfaces
    "IArticleFetcher",
    "IArticleScorer",
    "IMessageFormatter",
    "IMessageSender",
    # Result types
    "FetchResult",
    "ScoreResult",
    "SendResult",
]

