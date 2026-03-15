#!/usr/bin/env python3
"""CLI entry point — run the news pipeline on demand.

Usage:
    python fetch.py                          # Legacy health channel
    python fetch.py --channel ai-video       # Run a specific channel
    python fetch.py --channel ai-coding --dry-run  # Preview without sending
    python fetch.py --list-channels          # Show available channels
"""

import argparse
import sys

from src.utils import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Jal News — multi-topic news pipeline")
    parser.add_argument(
        "--channel", "-c",
        type=str,
        default="health",
        help="Channel slug to run (e.g. 'health', 'ai-video', 'ai-coding'). "
             "Loads config from channels/<slug>.yaml. Defaults to 'health'.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the full pipeline but print the message instead of sending.",
    )
    parser.add_argument(
        "--list-channels",
        action="store_true",
        help="List all available channel configurations and exit.",
    )
    args = parser.parse_args()

    setup_logging()

    if args.list_channels:
        from src.channels.loader import list_channels
        channels = list_channels()
        if channels:
            print("Available channels:")
            for slug in channels:
                print(f"  - {slug}")
        else:
            print("No channel configs found in channels/ directory.")
        sys.exit(0)

    from src.container import create_pipeline

    pipeline = create_pipeline(channel_slug=args.channel)
    success = pipeline.run(dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
