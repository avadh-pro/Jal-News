#!/usr/bin/env python3
"""CLI entry point — run the Jal News pipeline on demand.

Usage:
    python fetch.py           # Full pipeline, sends to WhatsApp
    python fetch.py --dry-run # Full pipeline, prints message only
"""

import argparse
import sys

from src.utils import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Jal News — daily health news pipeline")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the full pipeline but print the message instead of sending via WhatsApp",
    )
    args = parser.parse_args()

    setup_logging()

    from src.pipeline import run_pipeline

    success = run_pipeline(dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

