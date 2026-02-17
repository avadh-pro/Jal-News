"""Scorer factory — create scorers by provider name."""

from src.core.interfaces import IArticleScorer
from src.scorers.claude_scorer import ClaudeScorer


class ScorerFactory:
    """Factory for creating article scorers by provider name."""

    @staticmethod
    def create(provider: str, **kwargs) -> IArticleScorer:
        """Create an article scorer for the given provider.

        Args:
            provider: Scorer provider name (e.g. ``"claude"``).
            **kwargs: Provider-specific arguments forwarded to the scorer
                constructor (e.g. ``api_key``, ``model``, ``batch_size``).

        Returns:
            An ``IArticleScorer`` implementation.

        Raises:
            ValueError: If the provider is not recognised.
        """
        provider = provider.lower().strip()

        if provider == "claude":
            return ClaudeScorer(**kwargs)

        raise ValueError(
            f"Unknown scorer provider: {provider!r}. "
            f"Supported providers: 'claude'"
        )

