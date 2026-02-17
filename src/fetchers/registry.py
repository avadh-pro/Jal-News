"""Fetcher registry for runtime discovery of article fetchers."""

from __future__ import annotations

from src.core.interfaces import IArticleFetcher


class FetcherRegistry:
    """Registry that maps names to fetcher instances.

    Allows runtime registration and discovery of fetchers so that new
    sources can be added without modifying existing code.
    """

    _registry: dict[str, IArticleFetcher] = {}

    @classmethod
    def register(cls, name: str, fetcher: IArticleFetcher) -> None:
        """Register a fetcher under the given name.

        Args:
            name: Unique name for this fetcher.
            fetcher: An IArticleFetcher instance.
        """
        cls._registry[name] = fetcher

    @classmethod
    def get(cls, name: str) -> IArticleFetcher | None:
        """Retrieve a registered fetcher by name.

        Args:
            name: The name the fetcher was registered under.

        Returns:
            The fetcher instance, or None if not found.
        """
        return cls._registry.get(name)

    @classmethod
    def list_fetchers(cls) -> list[str]:
        """Return the names of all registered fetchers."""
        return list(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        """Remove all registered fetchers (useful for testing)."""
        cls._registry.clear()

