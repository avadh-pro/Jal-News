"""AI-powered article scorer using Anthropic Claude 3.5 Haiku."""

import json
import logging
import re
from typing import List

import anthropic

from src.config import settings
from src.models import Article, ScoredArticle

from .prompt import SYSTEM_PROMPT, build_scoring_prompt

logger = logging.getLogger(__name__)

MODEL = "claude-3-5-haiku-20241022"
BATCH_SIZE = 10
DEFAULT_TOP_N = 5


def _parse_scores(raw: str) -> list[dict]:
    """Extract and parse the JSON array from Claude's response.

    Handles cases where the model wraps JSON in markdown fences.
    """
    # Strip markdown code fences if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse scoring response as JSON: {e}")
        logger.debug(f"Raw response:\n{raw[:500]}")
        return []

    if not isinstance(data, list):
        logger.error("Scoring response is not a JSON array")
        return []

    return data


def _score_batch(
    client: anthropic.Anthropic,
    articles: List[Article],
    start_index: int,
) -> list[dict]:
    """Score a single batch of articles via the Claude API.

    Args:
        client: Anthropic client instance.
        articles: The batch of Article objects to score.
        start_index: The global index offset for this batch.

    Returns:
        List of score dicts with keys: index, shareability, novelty, relevance,
        viral_potential, summary.
    """
    batch_dicts = [
        {
            "index": start_index + i,
            "title": a.title,
            "description": a.description or "(no description)",
            "source_name": a.source_name,
        }
        for i, a in enumerate(articles)
    ]

    prompt = build_scoring_prompt(batch_dicts)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = response.content[0].text
        return _parse_scores(raw_text)
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error scoring batch at index {start_index}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error scoring batch at index {start_index}: {e}")
        return []


def score_articles(
    articles: list[Article],
    top_n: int = DEFAULT_TOP_N,
) -> list[ScoredArticle]:
    """Score and rank articles using Claude 3.5 Haiku.

    Articles are sent in batches to minimize API calls. Each article receives
    scores for shareability, novelty, relevance, and viral potential (1-10).
    A composite score (average of the four) is calculated for ranking.

    Args:
        articles: List of Article objects to score.
        top_n: Number of top-scoring articles to return (default: 5).

    Returns:
        Top N ScoredArticle objects sorted by composite score (highest first).
    """
    if not articles:
        logger.warning("No articles to score")
        return []

    if not settings.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY is not set — cannot score articles")
        return []

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Collect all score dicts across batches
    all_scores: list[dict] = []

    for batch_start in range(0, len(articles), BATCH_SIZE):
        batch = articles[batch_start : batch_start + BATCH_SIZE]
        logger.info(
            f"Scoring batch {batch_start // BATCH_SIZE + 1} "
            f"({len(batch)} articles, index {batch_start}-{batch_start + len(batch) - 1})"
        )
        scores = _score_batch(client, batch, batch_start)
        all_scores.extend(scores)

    # Map scores by index for lookup
    score_map: dict[int, dict] = {}
    for s in all_scores:
        idx = s.get("index")
        if idx is not None:
            score_map[int(idx)] = s

    # Build ScoredArticle list
    scored: list[ScoredArticle] = []
    for i, article in enumerate(articles):
        s = score_map.get(i)
        if s is None:
            logger.warning(f"No score returned for article {i}: {article.title[:60]}")
            # Assign a score of 0 so it sinks to the bottom
            scored.append(ScoredArticle.from_article(article, score=0.0, summary=""))
            continue

        composite = (
            s.get("shareability", 0)
            + s.get("novelty", 0)
            + s.get("relevance", 0)
            + s.get("viral_potential", 0)
        ) / 4.0

        scored.append(
            ScoredArticle.from_article(
                article,
                score=round(composite, 2),
                summary=s.get("summary", ""),
            )
        )

    # Sort by composite score descending, return top N
    scored.sort(key=lambda a: a.score, reverse=True)
    top = scored[:top_n]

    logger.info(
        f"Scored {len(scored)} articles — returning top {len(top)} "
        f"(best: {top[0].score if top else 'N/A'})"
    )
    return top
