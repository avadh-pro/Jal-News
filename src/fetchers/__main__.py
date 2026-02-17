"""Standalone runner for the fetchers module.

Usage:
    python -m src.fetchers
"""

import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)

from src.fetchers.composite import CompositeFetcher
from src.fetchers.newsapi_fetcher import NewsAPIFetcher
from src.fetchers.registry import FetcherRegistry
from src.fetchers.rss_fetcher import RSS_FEEDS, RSSFetcher


def main() -> None:
    print("=" * 80)
    print("  Health News Fetcher (SOLID) — Standalone Test Run")
    print("=" * 80)
    print()

    # Create individual RSS fetchers from config
    fetchers = []
    for feed in RSS_FEEDS:
        fetcher = RSSFetcher(name=feed["name"], url=feed["url"])
        FetcherRegistry.register(feed["name"], fetcher)
        fetchers.append(fetcher)

    # Add NewsAPI fetcher if key is available
    newsapi_key = os.environ.get("NEWSAPI_KEY", "")
    if newsapi_key:
        newsapi = NewsAPIFetcher(api_key=newsapi_key)
        FetcherRegistry.register("NewsAPI", newsapi)
        fetchers.append(newsapi)

    # Create composite fetcher
    composite = CompositeFetcher(fetchers=fetchers)

    print(f"Registered fetchers: {FetcherRegistry.list_fetchers()}")
    print()

    # Fetch all articles
    articles = composite.fetch()

    if not articles:
        print("No articles fetched. Check logs above for errors.")
        sys.exit(1)

    print(f"\n{'=' * 80}")
    print(f"  Fetched {len(articles)} unique articles")
    print(f"{'=' * 80}\n")

    for i, article in enumerate(articles, 1):
        pub_str = article.published_at.strftime("%Y-%m-%d %H:%M UTC")
        print(f"[{i:3d}] {article.title}")
        print(f"      Source: {article.source_name}")
        print(f"      Date:   {pub_str}")
        print(f"      URL:    {article.url}")
        if article.description:
            desc = article.description[:150]
            if len(article.description) > 150:
                desc += "..."
            print(f"      Desc:   {desc}")
        print()


if __name__ == "__main__":
    main()

