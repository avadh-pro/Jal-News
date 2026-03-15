"""Sent-article tracker for deduplication.

Stores URLs of previously sent articles in a local JSON file so the
pipeline never sends the same article twice.

NOTE: The .sent_articles.json file is local state and will NOT persist
between GitHub Actions runs (each run starts with a clean checkout).
The 3-day date filter in the fetchers still works in that environment;
deduplication is an additional optimization for local / persistent runs.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.models import Article

logger = logging.getLogger(__name__)

_DEFAULT_STORAGE = ".sent_articles.json"
_CLEANUP_DAYS = 30


def storage_path_for_channel(channel_slug: str | None = None) -> str:
    """Return the dedup storage path for a given channel.

    Args:
        channel_slug: Channel identifier. When None, uses the default path.

    Returns:
        Path string like ``.sent_articles_ai-video.json``.
    """
    if not channel_slug:
        return _DEFAULT_STORAGE
    return f".sent_articles_{channel_slug}.json"


class SentArticleTracker:
    """Tracks URLs of articles already sent to avoid duplicates.

    Args:
        storage_path: Path to the JSON file used for persistence.
            Defaults to ``.sent_articles.json`` in the working directory.
    """

    def __init__(self, storage_path: str = _DEFAULT_STORAGE) -> None:
        self._storage_path = Path(storage_path)
        # Map of url -> ISO-8601 timestamp when the URL was recorded
        self._sent: dict[str, str] = {}
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_sent(self, url: str) -> bool:
        """Return True if *url* has already been sent."""
        return url in self._sent

    def mark_sent(self, urls: list[str]) -> None:
        """Record *urls* as sent and persist to disk."""
        now = datetime.now(timezone.utc).isoformat()
        for url in urls:
            self._sent[url] = now
        self._cleanup()
        self._save()
        logger.info("Marked %d article URL(s) as sent", len(urls))

    def filter_unsent(self, articles: list[Article]) -> list[Article]:
        """Return only articles whose URL has not been sent before."""
        unsent = [a for a in articles if not self.is_sent(a.url)]
        filtered = len(articles) - len(unsent)
        if filtered:
            logger.info(
                "Dedup: %d articles filtered, %d remaining",
                filtered, len(unsent),
            )
        return unsent

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load sent URLs from the JSON file."""
        if not self._storage_path.exists():
            return
        try:
            data = json.loads(self._storage_path.read_text(encoding="utf-8"))
            # Support both old format (list of urls) and new format (dict url->timestamp)
            if isinstance(data.get("urls"), dict):
                self._sent = data["urls"]
            elif isinstance(data.get("urls"), list):
                # Migrate from old list format
                now = datetime.now(timezone.utc).isoformat()
                self._sent = {url: now for url in data["urls"]}
            logger.debug("Loaded %d sent URLs from %s", len(self._sent), self._storage_path)
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning("Failed to load sent articles from %s: %s", self._storage_path, exc)

    def _save(self) -> None:
        """Persist sent URLs to the JSON file."""
        data = {
            "urls": self._sent,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._storage_path.write_text(
            json.dumps(data, indent=2, sort_keys=True), encoding="utf-8"
        )

    def _cleanup(self) -> None:
        """Remove entries older than 30 days to prevent file bloat."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=_CLEANUP_DAYS)
        before = len(self._sent)
        self._sent = {
            url: ts
            for url, ts in self._sent.items()
            if self._parse_ts(ts) >= cutoff
        }
        removed = before - len(self._sent)
        if removed:
            logger.info("Dedup cleanup: removed %d stale entries (>%d days)", removed, _CLEANUP_DAYS)

    @staticmethod
    def _parse_ts(ts: str) -> datetime:
        """Parse an ISO-8601 timestamp string, falling back to epoch on error."""
        try:
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            return datetime.min.replace(tzinfo=timezone.utc)

