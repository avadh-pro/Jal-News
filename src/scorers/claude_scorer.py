"""Claude-based article scorer using Anthropic API."""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING

import anthropic

from src.core.models import Article
from src.scorers.base import BaseScorer
from src.scorers.prompt import build_scoring_prompt, build_system_prompt

if TYPE_CHECKING:
    from src.channels.channel import Channel

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-haiku-4-5-20251001"


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


class ClaudeScorer(BaseScorer):
    """Article scorer powered by Anthropic Claude.

    Args:
        api_key: Anthropic API key.
        model: Model identifier (default: claude-haiku-4-5-20251001).
        batch_size: Number of articles per API call (default: 10).
        channel: Optional channel config for topic-specific scoring prompts.
    """

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        batch_size: int = 10,
        channel: Channel | None = None,
    ) -> None:
        super().__init__(batch_size=batch_size)
        self.model = model
        self._client = anthropic.Anthropic(api_key=api_key)
        self._channel = channel

    def _score_batch(
        self,
        articles: list[Article],
        start_index: int,
    ) -> list[dict]:
        """Score a single batch of articles via the Claude API."""
        batch_dicts = [
            {
                "index": i,
                "title": a.title,
                "description": a.description or "(no description)",
                "source_name": a.source_name,
                "source_tier": a.source_tier,
                "coverage_count": a.coverage_count,
            }
            for i, a in enumerate(articles)
        ]

        prompt = build_scoring_prompt(batch_dicts, channel=self._channel)
        system = build_system_prompt(channel=self._channel)

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = response.content[0].text
            parsed = _parse_scores(raw_text)
            # Convert 0-based local indices to global indices
            for entry in parsed:
                if "index" in entry:
                    entry["index"] = start_index + int(entry["index"])
            return parsed
        except anthropic.APIError as e:
            logger.error(
                f"Anthropic API error scoring batch at index {start_index}: {e}"
            )
            return []
        except Exception as e:
            logger.error(
                f"Unexpected error scoring batch at index {start_index}: {e}"
            )
            return []
