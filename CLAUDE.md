# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jal News is an AI-powered health news curator for Amaro Labs. It fetches health articles from 9 RSS feeds + NewsAPI, scores them with Claude 3 Haiku, and delivers top picks to Telegram.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# One-time run (preview without sending)
python fetch.py --dry-run

# One-time run (sends to Telegram)
python fetch.py

# Daily scheduler (runs at SCHEDULE_TIME from .env)
python main.py

# Test individual modules
python -m src.fetchers
python -m src.scorers
python -m src.senders
```

## Required Environment Variables

Copy `.env.example` to `.env`. Required keys: `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. Optional: `NEWSAPI_KEY`, `SCHEDULE_TIME` (default 07:00), `TOP_N_ARTICLES` (default 5), `ENABLE_DEDUP` (default true).

## Architecture

**Pipeline flow:** Fetch → Deduplicate → Score → Format → Send

```
src/
├── core/           # Domain models (Article, ScoredArticle) and interfaces (IArticleFetcher, IArticleScorer, IMessageSender, IMessageFormatter)
├── fetchers/       # CompositeFetcher aggregates 9 RSSFetchers + NewsAPIFetcher in parallel via ThreadPoolExecutor, deduplicates by URL/title similarity
├── scorers/        # ClaudeScorer batches articles to Claude 3 Haiku, scores on shareability/novelty/relevance/viral_potential (1-10)
├── formatters/     # TelegramFormatter renders Markdown with emojis, respects 4096-char limit
├── senders/        # TelegramSender with retry logic (2 retries default)
├── pipeline/       # NewsPipeline orchestrator + PipelineBuilder (fluent interface)
├── dedup/          # SentArticleTracker persists sent URLs to .sent_articles.json, auto-cleans entries >30 days
├── config/         # Settings dataclass loaded from env vars
└── container.py    # DI wiring — create_pipeline() builds the full pipeline with all 9 RSS sources
```

**Entry points:** `fetch.py` (CLI, one-time) and `main.py` (scheduled via `schedule` library).

**Key design:** SOLID architecture with dependency inversion — `NewsPipeline` depends on interfaces, not concrete implementations. Uses Strategy (swappable scorers/senders), Composite (aggregated fetchers), Factory, Registry, and Builder patterns. Adding a new source or delivery channel means implementing the relevant interface and registering it in `container.py`.

**Error resilience:** Individual source failures are logged and skipped; the pipeline continues with successful sources.
