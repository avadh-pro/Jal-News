"""Daily news pipeline — fetch, score, and deliver health news.

Exports the new SOLID-compliant pipeline classes alongside a backward-
compatible ``run_pipeline()`` convenience function.
"""

from src.pipeline.builder import PipelineBuilder
from src.pipeline.pipeline import NewsPipeline

__all__ = ["NewsPipeline", "PipelineBuilder", "run_pipeline"]


def run_pipeline(dry_run: bool = False) -> bool:
    """Execute the full news pipeline: fetch → score → send.

    This is a backward-compatible convenience wrapper that creates a
    fully configured pipeline via the DI container and runs it.

    Args:
        dry_run: If True, format and log but do not actually send.

    Returns:
        True if the pipeline completed successfully, False otherwise.
    """
    from src.container import create_pipeline

    pipeline = create_pipeline()
    return pipeline.run(dry_run=dry_run)
