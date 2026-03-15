"""Channel configuration — defines topic-specific news pipelines."""

from src.channels.channel import Channel
from src.channels.loader import load_channel, list_channels

__all__ = ["Channel", "load_channel", "list_channels"]
