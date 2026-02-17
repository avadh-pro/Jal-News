"""Fluent builder for constructing a NewsPipeline."""

from __future__ import annotations

from src.core.interfaces import IArticleFetcher, IArticleScorer, IMessageSender
from src.pipeline.pipeline import NewsPipeline


class PipelineBuilder:
    """Fluent builder that assembles a :class:`NewsPipeline` step by step.

    Example::

        pipeline = (
            PipelineBuilder()
            .with_fetcher(composite_fetcher)
            .with_scorer(claude_scorer)
            .with_sender(telegram_sender)
            .build()
        )
    """

    def __init__(self) -> None:
        self._fetcher: IArticleFetcher | None = None
        self._scorer: IArticleScorer | None = None
        self._sender: IMessageSender | None = None

    def with_fetcher(self, fetcher: IArticleFetcher) -> PipelineBuilder:
        """Set the article fetcher.

        Args:
            fetcher: An IArticleFetcher implementation.

        Returns:
            Self for method chaining.
        """
        self._fetcher = fetcher
        return self

    def with_scorer(self, scorer: IArticleScorer) -> PipelineBuilder:
        """Set the article scorer.

        Args:
            scorer: An IArticleScorer implementation.

        Returns:
            Self for method chaining.
        """
        self._scorer = scorer
        return self

    def with_sender(self, sender: IMessageSender) -> PipelineBuilder:
        """Set the message sender.

        Args:
            sender: An IMessageSender implementation.

        Returns:
            Self for method chaining.
        """
        self._sender = sender
        return self

    def build(self) -> NewsPipeline:
        """Build and return the configured :class:`NewsPipeline`.

        Raises:
            ValueError: If any required component is missing.

        Returns:
            A fully configured NewsPipeline instance.
        """
        missing: list[str] = []
        if self._fetcher is None:
            missing.append("fetcher")
        if self._scorer is None:
            missing.append("scorer")
        if self._sender is None:
            missing.append("sender")

        if missing:
            raise ValueError(
                f"Cannot build pipeline — missing components: {', '.join(missing)}"
            )

        return NewsPipeline(
            fetcher=self._fetcher,  # type: ignore[arg-type]
            scorer=self._scorer,  # type: ignore[arg-type]
            sender=self._sender,  # type: ignore[arg-type]
        )

