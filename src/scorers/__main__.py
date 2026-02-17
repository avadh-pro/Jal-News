"""Standalone runner for the scorers module.

Usage:
    python -m src.scorers
"""

import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)

from src.fetcher import fetch_all_articles
from src.scorers import ClaudeScorer


def main() -> None:
    print("=" * 80)
    print("  AI Article Scorer — Standalone Test Run (SOLID refactor)")
    print("=" * 80)
    print()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        sys.exit(1)

    # Step 1: Fetch articles using the old fetcher
    print("Fetching articles...")
    articles = fetch_all_articles()

    if not articles:
        print("No articles fetched. Check logs above for errors.")
        sys.exit(1)

    print(f"Fetched {len(articles)} articles. Scoring with ClaudeScorer...\n")

    # Step 2: Score articles
    scorer = ClaudeScorer(api_key=api_key)
    top_articles = scorer.score(articles, top_n=5)

    if not top_articles:
        print("Scoring failed — no scored articles returned. Check logs.")
        sys.exit(1)

    # Step 3: Display results
    print(f"\n{'=' * 80}")
    print(f"  🏆 Top {len(top_articles)} Articles by AI Score")
    print(f"{'=' * 80}\n")

    for rank, article in enumerate(top_articles, 1):
        pub_str = article.published_at.strftime("%Y-%m-%d %H:%M UTC")
        print(f"#{rank}  [Score: {article.score}/10]  {article.title}")
        print(f"     Source:  {article.source_name}")
        print(f"     Date:    {pub_str}")
        print(f"     URL:     {article.url}")
        if article.summary:
            print(f"     Summary: {article.summary}")
        print()

    print(f"{'=' * 80}")
    print(f"  Scored {len(articles)} articles → Top {len(top_articles)} shown above")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()

