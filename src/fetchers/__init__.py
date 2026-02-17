"""Fetchers module — SOLID-compliant article fetcher implementations."""

from src.fetchers.composite import CompositeFetcher
from src.fetchers.newsapi_fetcher import NewsAPIFetcher
from src.fetchers.registry import FetcherRegistry
from src.fetchers.rss_fetcher import RSSFetcher

__all__ = [
    "RSSFetcher",
    "NewsAPIFetcher",
    "CompositeFetcher",
    "FetcherRegistry",
]

