"""WhatsApp message sender using Meta WhatsApp Cloud API."""

import logging
from dataclasses import dataclass
from typing import Optional

import requests

from src.config import settings
from src.models import ScoredArticle
from src.sender.formatter import format_digest

__all__ = ["send_whatsapp_message"]

logger = logging.getLogger(__name__)

_API_URL = "https://graph.facebook.com/v18.0/{phone_number_id}/messages"
_MAX_RETRIES = 2


@dataclass
class SendResult:
    """Outcome of a WhatsApp send attempt."""

    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


def _send_via_api(message: str) -> SendResult:
    """Send a text message through the WhatsApp Cloud API.

    Makes a POST request to the Meta Graph API with up to
    ``_MAX_RETRIES`` retry attempts on failure.
    """
    url = _API_URL.format(phone_number_id=settings.whatsapp_phone_number_id)
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": settings.recipient_phone_number,
        "type": "text",
        "text": {"body": message},
    }

    last_error = ""
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                msg_id = data.get("messages", [{}])[0].get("id", "unknown")
                logger.info("WhatsApp message sent successfully (id=%s)", msg_id)
                return SendResult(success=True, message_id=msg_id)

            last_error = f"HTTP {resp.status_code}: {resp.text}"
            logger.warning(
                "WhatsApp API error (attempt %d/%d): %s",
                attempt,
                _MAX_RETRIES,
                last_error,
            )
        except requests.RequestException as exc:
            last_error = str(exc)
            logger.warning(
                "WhatsApp request failed (attempt %d/%d): %s",
                attempt,
                _MAX_RETRIES,
                last_error,
            )

    logger.error("WhatsApp delivery failed after %d attempts: %s", _MAX_RETRIES, last_error)
    return SendResult(success=False, error=last_error)


def send_whatsapp_message(
    articles: list[ScoredArticle],
    dry_run: bool = False,
) -> SendResult:
    """Format and send a WhatsApp digest of scored articles.

    Args:
        articles: Ranked articles to include in the digest.
        dry_run: If ``True``, print the message to stdout instead of sending.

    Returns:
        A :class:`SendResult` indicating success or failure.
    """
    if not articles:
        logger.warning("No articles to send")
        return SendResult(success=False, error="No articles provided")

    message = format_digest(articles)
    logger.info("Formatted digest (%d chars, %d articles)", len(message), len(articles))

    if dry_run:
        print("\n" + "=" * 50)
        print("DRY RUN — WhatsApp message preview:")
        print("=" * 50)
        print(message)
        print("=" * 50 + "\n")
        return SendResult(success=True, message_id="dry-run")

    # Validate required config before attempting to send
    missing = []
    if not settings.whatsapp_phone_number_id:
        missing.append("WHATSAPP_PHONE_NUMBER_ID")
    if not settings.whatsapp_access_token:
        missing.append("WHATSAPP_ACCESS_TOKEN")
    if not settings.recipient_phone_number:
        missing.append("RECIPIENT_PHONE_NUMBER")
    if missing:
        error = f"Missing required env vars: {', '.join(missing)}"
        logger.error(error)
        return SendResult(success=False, error=error)

    return _send_via_api(message)
