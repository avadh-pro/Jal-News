"""Senders module — message sending strategies for different platforms."""

from src.senders.factory import SenderFactory
from src.senders.telegram_sender import TelegramSender

__all__ = ["TelegramSender", "SenderFactory"]

