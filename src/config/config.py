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

    # WhatsApp Cloud API (Meta)
    whatsapp_phone_number_id: str = field(
        default_factory=lambda: os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    )
    whatsapp_access_token: str = field(
        default_factory=lambda: os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    )

    # Recipient
    recipient_phone_number: str = field(
        default_factory=lambda: os.getenv("RECIPIENT_PHONE_NUMBER", "")
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
            "WHATSAPP_PHONE_NUMBER_ID": self.whatsapp_phone_number_id,
            "WHATSAPP_ACCESS_TOKEN": self.whatsapp_access_token,
            "RECIPIENT_PHONE_NUMBER": self.recipient_phone_number,
        }
        return [key for key, value in required.items() if not value]


# Singleton instance
settings = Settings()

