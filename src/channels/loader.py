"""Load channel configurations from YAML files in the channels/ directory."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from src.channels.channel import Channel

logger = logging.getLogger(__name__)

# Default channels directory at project root
_CHANNELS_DIR = Path(__file__).resolve().parent.parent.parent / "channels"


def load_channel(slug: str, channels_dir: Path | None = None) -> Channel:
    """Load a channel configuration by slug.

    Args:
        slug: The channel identifier (matches the YAML filename without extension).
        channels_dir: Directory containing channel YAML files.

    Returns:
        A fully populated Channel instance.

    Raises:
        FileNotFoundError: If no YAML file exists for the given slug.
        ValueError: If the YAML file is missing required fields.
    """
    base = channels_dir or _CHANNELS_DIR
    path = base / f"{slug}.yaml"

    if not path.exists():
        available = list_channels(base)
        raise FileNotFoundError(
            f"Channel '{slug}' not found at {path}. "
            f"Available channels: {available}"
        )

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Channel file {path} must contain a YAML mapping")

    name = data.get("name")
    if not name:
        raise ValueError(f"Channel '{slug}' is missing required 'name' field")

    return Channel(
        slug=slug,
        name=name,
        feeds=data.get("feeds", []),
        newsapi_query=data.get("newsapi_query", ""),
        newsapi_domains=data.get("newsapi_domains", ""),
        scoring_system_prompt=data.get("scoring", {}).get("system_prompt", ""),
        scoring_relevance_hint=data.get("scoring", {}).get("relevance_hint", ""),
        header_emoji=data.get("formatting", {}).get("header_emoji", "📰"),
        category_emojis=data.get("formatting", {}).get(
            "category_emojis", ["📰", "🔍", "💡", "⚡", "🌐"]
        ),
        footer_text=data.get("formatting", {}).get("footer_text", "Curated by AI"),
        telegram_chat_id=data.get("telegram_chat_id", ""),
        schedule_time=data.get("schedule_time", ""),
        top_n=data.get("top_n", 5),
    )


def list_channels(channels_dir: Path | None = None) -> list[str]:
    """Return slugs of all available channel configs."""
    base = channels_dir or _CHANNELS_DIR
    if not base.exists():
        return []
    return sorted(p.stem for p in base.glob("*.yaml"))
