"""Standalone runner for the fetchers module.

Usage:
    python -m src.fetchers                    # Default health feeds
    python -m src.fetchers --channel ai-video # Channel-specific feeds
"""

import argparse
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
from src.fetchers.rss_fetcher import RSSFetcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetcher test runner")
    parser.add_argument("--channel", "-c", type=str, default=None)
    args = parser.parse_args()

    # Load feeds from channel config or fall back to legacy
    if args.channel:
        from src.channels.loader import load_channel
        channel = load_channel(args.channel)
        feeds = channel.feeds
        title = channel.name
    else:
        from src.container import _LEGACY_RSS_FEEDS
        feeds = _LEGACY_RSS_FEEDS
        title = "Health News Fetcher"

    print("=" * 80)
    print(f"  {title} — Standalone Test Run")
    print("=" * 80)
    print()

    # Create individual RSS fetchers from config
    fetchers = []
    for feed in feeds:
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
