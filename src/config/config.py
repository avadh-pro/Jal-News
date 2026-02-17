"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


@dataclass(frozen=True)
class Settings:
    """Immutable application settings loaded from environment variables."""

    # Anthropic Claude API
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))

    # NewsAPI.org
    newsapi_key: str = field(default_factory=lambda: os.getenv("NEWSAPI_KEY", ""))

    # Telegram Bot API
    telegram_bot_token: str = field(
        default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", "")
    )
    telegram_chat_id: str = field(
        default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", "")
    )

    # Schedule
    schedule_time: str = field(default_factory=lambda: os.getenv("SCHEDULE_TIME", "07:00"))

    # Top N articles
    top_n_articles: int = field(
        default_factory=lambda: int(os.getenv("TOP_N_ARTICLES", "5"))
    )

    def validate(self) -> list[str]:
        """Return a list of missing required configuration keys."""
        required = {
            "ANTHROPIC_API_KEY": self.anthropic_api_key,
            "NEWSAPI_KEY": self.newsapi_key,
            "TELEGRAM_BOT_TOKEN": self.telegram_bot_token,
            "TELEGRAM_CHAT_ID": self.telegram_chat_id,
        }
        return [key for key, value in required.items() if not value]


# Singleton instance
settings = Settings()

