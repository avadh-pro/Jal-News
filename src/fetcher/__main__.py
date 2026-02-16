"""Standalone runner for the news fetcher module.

Usage:
    python -m src.fetcher
"""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)

from src.fetcher import fetch_all_articles


def main() -> None:
    print("=" * 80)
    print("  Health News Fetcher — Standalone Test Run")
    print("=" * 80)
    print()

    articles = fetch_all_articles()

    if not articles:
        print("No articles fetched. Check logs above for errors.")
        sys.exit(1)

    print(f"\n{'=' * 80}")
    print(f"  Fetched {len(articles)} unique articles (last 24 hours)")
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

    # Summary by source
    sources: dict[str, int] = {}
    for article in articles:
        sources[article.source_name] = sources.get(article.source_name, 0) + 1

    print(f"{'=' * 80}")
    print("  Articles by Source:")
    print(f"{'=' * 80}")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source:30s} : {count} articles")
    print(f"{'=' * 80}")
    print(f"  Total: {len(articles)} articles")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()

