"""NewsAPI.org fetcher for mainstream health news."""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import requests
from dateutil import parser as dateutil_parser

from src.models import Article

logger = logging.getLogger(__name__)

NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"
NEWSAPI_HEALTH_QUERY = (
    '"health news" OR "medical research" OR "clinical trial" '
    'OR "public health" OR "physiotherapy" OR "healthcare"'
)
NEWSAPI_PAGE_SIZE = 50


def _parse_newsapi_date(date_str: Optional[str]) -> datetime:
    """Parse a date string from NewsAPI response."""
    if not date_str:
        return datetime.now(timezone.utc)
    try:
        dt = dateutil_parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


def fetch_newsapi(api_key: Optional[str] = None) -> List[Article]:
    """Fetch health news articles from NewsAPI.org.

    Args:
        api_key: NewsAPI API key. Falls back to NEWSAPI_KEY env var.

    Returns:
        List of Article objects from NewsAPI.
    """
    api_key = api_key or os.environ.get("NEWSAPI_KEY", "")
    if not api_key:
        logger.warning("No NewsAPI key configured (set NEWSAPI_KEY env var). Skipping NewsAPI.")
        return []

    logger.info("Fetching articles from NewsAPI.org")

    # Fetch articles from the last 24 hours
    from_date = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "q": NEWSAPI_HEALTH_QUERY,
        "from": from_date,
        "sortBy": "publishedAt",
        "pageSize": NEWSAPI_PAGE_SIZE,
        "language": "en",
        "apiKey": api_key,
    }

    try:
        response = requests.get(NEWSAPI_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            logger.error(f"NewsAPI returned error: {data.get('message', 'Unknown error')}")
            return []

        articles: List[Article] = []
        for item in data.get("articles", []):
            title = (item.get("title") or "").strip()
            if not title or title == "[Removed]":
                continue

            description = (item.get("description") or "").strip()
            url = (item.get("url") or "").strip()
            if not url:
                continue

            source_name = item.get("source", {}).get("name", "NewsAPI")
            published_at = _parse_newsapi_date(item.get("publishedAt"))
            image_url = item.get("urlToImage")

            articles.append(
                Article(
                    title=title,
                    description=description,
                    url=url,
                    source_name=source_name,
                    published_at=published_at,
                    image_url=image_url,
                )
            )

        logger.info(f"Fetched {len(articles)} articles from NewsAPI")
        return articles

    except requests.exceptions.Timeout:
        logger.error("NewsAPI request timed out")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching from NewsAPI: {e}")
        return []
    except (ValueError, KeyError) as e:
        logger.error(f"Error parsing NewsAPI response: {e}")
        return []

