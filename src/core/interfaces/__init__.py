"""Abstract interfaces for the news curation pipeline."""

from src.core.interfaces.fetcher import IArticleFetcher
from src.core.interfaces.formatter import IMessageFormatter
from src.core.interfaces.scorer import IArticleScorer
from src.core.interfaces.sender import IMessageSender

__all__ = [
    "IArticleFetcher",
    "IArticleScorer",
    "IMessageFormatter",
    "IMessageSender",
]

