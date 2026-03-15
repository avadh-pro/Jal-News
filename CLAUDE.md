# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jal News is an AI-powered multi-topic news curator. It fetches articles from RSS feeds + NewsAPI, scores them with Claude Haiku 4.5 on five dimensions (including source credibility), and delivers curated digests to Telegram. Supports any topic via YAML channel configs with tiered source credibility.

## Commands

```bash
pip install -r requirements.txt

# Run a specific channel
python fetch.py --channel ai-news
python fetch.py --channel health --dry-run

# List available channels
python fetch.py --list-channels

# Daily scheduler
python main.py --channel ai-coding       # single channel
python main.py --all                      # all channels

# Test individual modules
python -m src.fetchers --channel ai-video
python -m src.scorers
python -m src.senders
```

## Environment Variables

Copy `.env.example` to `.env`. Required: `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. Optional: `NEWSAPI_KEY`, `SCHEDULE_TIME` (default 07:00), `TOP_N_ARTICLES` (default 5), `ENABLE_DEDUP` (default true).

## Architecture

**Pipeline flow:** Fetch (parallel) → Deduplicate (with coverage tracking) → Score (5 dimensions) → Format → Send

### Channel system

Each topic is a YAML file in `channels/` with:
- RSS feeds with `tier` and `weight` per source (primary > expert > major-outlet > niche > community > aggregator)
- NewsAPI query + `newsapi_domains` whitelist
- AI scorer system prompt and relevance criteria
- Formatter branding (header emoji, category emojis, footer text)
- Optional per-channel Telegram chat ID, schedule time, top_n

Current channels: `ai-news`, `ai-video`, `ai-music`, `ai-coding`, `ai-motion-graphics`, `health`.

To add a new topic: create `channels/<slug>.yaml` following existing examples. No code changes needed.

### Credibility system

Source credibility flows through three layers:
1. **Feed config:** Each RSS feed has a `tier` label and `credibility_weight` (0.0-1.0) multiplier
2. **Scorer prompt:** `source_credibility` is the 5th scoring dimension (1-10). Claude sees the source tier and coverage count in the prompt.
3. **Composite score:** Weighted formula (novelty 25%, relevance 25%, credibility 20%, shareability 20%, viral 10%) × `credibility_weight` × coverage bonus (up to +25% for multi-source stories)

### Coverage tracking

`CompositeFetcher` counts how many outlets report the same story before deduplication. It keeps the version from the highest-weight source and attaches `coverage_count` to the article. Stories covered by multiple outlets get a score boost.

### Key modules

- **Entry points:** `fetch.py` (CLI) and `main.py` (scheduler)
- **DI wiring:** `src/container.py` — `create_pipeline(channel_slug="...")` builds the full pipeline
- **Channel loading:** `src/channels/loader.py` reads YAML from `channels/` dir
- **Scoring:** 5 dimensions with weighted composite. Model: `claude-haiku-4-5-20251001`
- **Dedup:** Per-channel files (`.sent_articles_<slug>.json`), auto-cleans entries >30 days
- **NewsAPI:** Supports custom query + `domains=` whitelist per channel

## CI/CD

GitHub Actions (`.github/workflows/daily-news.yml`) runs every 2 days at 1:30 AM UTC. Supports manual dispatch with a `channel` input. Defaults to `health` channel.
