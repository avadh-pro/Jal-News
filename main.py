#!/usr/bin/env python3
"""Scheduler entry point — runs the Jal News pipeline daily.

Usage:
    python main.py  # Starts scheduler, runs daily at configured time
"""

import logging
import time

import schedule

from src.config import settings
from src.pipeline import run_pipeline
from src.utils import setup_logging

logger = logging.getLogger(__name__)


def _job() -> None:
    """Scheduled job wrapper."""
    logger.info("Scheduled run triggered")
    try:
        success = run_pipeline()
        if success:
            logger.info("Scheduled run completed successfully")
        else:
            logger.warning("Scheduled run finished with errors")
    except Exception as exc:
        logger.error("Scheduled run crashed: %s", exc, exc_info=True)


def main() -> None:
    setup_logging()

    run_time = settings.schedule_time  # e.g. "07:00"
    schedule.every().day.at(run_time).do(_job)

    logger.info("Jal News scheduler started — next run at %s daily", run_time)
    logger.info("Press Ctrl+C to stop")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


if __name__ == "__main__":
    main()

