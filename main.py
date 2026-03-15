#!/usr/bin/env python3
"""Scheduler entry point — runs the news pipeline on a schedule.

Usage:
    python main.py                      # Legacy: single health channel
    python main.py --channel ai-video   # Schedule a specific channel
    python main.py --all                # Schedule ALL configured channels
"""

import argparse
import logging
import time

import schedule

from src.config import settings
from src.utils import setup_logging

logger = logging.getLogger(__name__)


def _run_channel(channel_slug: str | None) -> None:
    """Run a single channel pipeline."""
    label = channel_slug or "default"
    logger.info("Scheduled run triggered for channel: %s", label)
    try:
        from src.container import create_pipeline
        pipeline = create_pipeline(channel_slug=channel_slug)
        success = pipeline.run()
        if success:
            logger.info("Channel '%s' completed successfully", label)
        else:
            logger.warning("Channel '%s' finished with errors", label)
    except Exception as exc:
        logger.error("Channel '%s' crashed: %s", label, exc, exc_info=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Jal News scheduler")
    parser.add_argument(
        "--channel", "-c",
        type=str,
        default="health",
        help="Run a specific channel on schedule. Defaults to 'health'.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Schedule ALL configured channels.",
    )
    args = parser.parse_args()

    setup_logging()

    if args.all:
        from src.channels.loader import list_channels, load_channel
        slugs = list_channels()
        if not slugs:
            logger.error("No channel configs found in channels/ directory.")
            return

        for slug in slugs:
            ch = load_channel(slug)
            run_time = ch.schedule_time or settings.schedule_time
            schedule.every().day.at(run_time).do(_run_channel, channel_slug=slug)
            logger.info("Scheduled channel '%s' at %s daily", slug, run_time)
    else:
        run_time = settings.schedule_time
        schedule.every().day.at(run_time).do(_run_channel, channel_slug=args.channel)
        label = args.channel or "default"
        logger.info("Scheduled channel '%s' at %s daily", label, run_time)

    logger.info("Scheduler started — press Ctrl+C to stop")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


if __name__ == "__main__":
    main()
