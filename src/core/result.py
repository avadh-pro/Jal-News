"""Result types for pipeline operations.

Each result type is an immutable (frozen) dataclass that captures
success/failure state along with operation-specific data.
"""

from dataclasses import dataclass, field
from typing import Optional

from src.core.models import Article, ScoredArticle


@dataclass(frozen=True)
class FetchResult:
    """Result of an article fetch operation."""

    success: bool
    articles: list[Article] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScoreResult:
    """Result of an article scoring operation."""

    success: bool
    scored_articles: list[ScoredArticle] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SendResult:
    """Result of a message send operation."""

    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None

