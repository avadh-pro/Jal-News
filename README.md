# 🩺 Jal News — AI-Powered Health News Curator

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4.svg)](https://core.telegram.org/bots/api)
[![Anthropic Claude](https://img.shields.io/badge/AI-Claude%203%20Haiku-orange.svg)](https://www.anthropic.com/)

An automated daily health news curator built for **Amaro Labs** — a health & wellness content channel. Jal News fetches the latest health news from 9+ vetted sources, uses Claude AI to identify the most groundbreaking stories, and delivers a curated digest to Telegram every morning.

> **Built with SOLID principles** — extensible, testable, and production-ready.

---

## ✨ Features

- **9 RSS Sources** — ScienceDaily, BBC Health, Medical Xpress, WHO, STAT News, ET HealthWorld, PhysioUpdate, CDC Newsroom, Health Affairs
- **NewsAPI Integration** — Aggregates additional health articles from 80,000+ sources
- **AI-Powered Scoring** — Claude 3 Haiku evaluates articles for newsworthiness, shareability, and relevance
- **Telegram Delivery** — Beautifully formatted daily digest sent via Telegram Bot API (free, unlimited)
- **Daily Scheduling** — Configurable daily runs (default: 7:00 AM IST)
- **Dry-Run Mode** — Preview the digest without sending
- **Graceful Error Handling** — Failed sources don't crash the pipeline; errors are logged and skipped
- **SOLID Architecture** — Clean interfaces, dependency injection, strategy pattern for easy extensibility
- **< $0.01/day** — Extremely cost-effective (only Anthropic API costs; Telegram is free)

---

## 🏗️ Architecture

Jal News follows **SOLID principles** with a clean, interface-driven architecture:

```
[9 RSS Feeds + NewsAPI] → CompositeFetcher → [Raw Articles]
                                                    ↓
                                             ClaudeScorer (AI)
                                                    ↓
                                            [Top 5 Ranked Articles]
                                                    ↓
                                        TelegramSender + Formatter
                                                    ↓
                                              Telegram 📱
```

### Design Patterns

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Strategy** | Scorers, Senders, Formatters | Swap AI providers or delivery channels |
| **Composite** | `CompositeFetcher` | Aggregate multiple fetchers into one |
| **Dependency Injection** | `NewsPipeline` | Pipeline depends on abstractions, not implementations |
| **Factory** | `ScorerFactory`, `SenderFactory` | Create components from configuration |
| **Registry** | `FetcherRegistry` | Discover and register fetcher implementations |

### Core Interfaces

```python
IArticleFetcher   →  Fetch articles from any source
IArticleScorer    →  Score/rank articles with any AI provider
IMessageSender    →  Send digests to any channel
IMessageFormatter →  Format messages for any platform
```

---

## 📋 Prerequisites

- **Python 3.11+**
- **Anthropic API Key** — [Get one here](https://console.anthropic.com/) (Claude 3 Haiku access)
- **Telegram Bot Token** — [Create a bot via @BotFather](https://t.me/BotFather) (free, takes 2 minutes)
- **Telegram Chat ID** — Your personal or group chat ID
- **NewsAPI Key** *(optional)* — [Get a free key](https://newsapi.org/) (100 requests/day)

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/avadh-pro/Jal-News.git
cd Jal-News

# 2. Switch to the feature branch
git checkout amaro-labs-health-news-app

# 3. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration section below)
```

---

## ⚙️ Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env` and fill in your values:

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | ✅ | Your Anthropic API key for Claude AI scoring | — |
| `TELEGRAM_BOT_TOKEN` | ✅ | Telegram Bot API token from @BotFather | — |
| `TELEGRAM_CHAT_ID` | ✅ | Target Telegram chat ID for digest delivery | — |
| `NEWSAPI_KEY` | ❌ | NewsAPI.org API key for additional sources | — |
| `SCHEDULE_TIME` | ❌ | Daily run time in 24h format (IST) | `07:00` |
| `TOP_N_ARTICLES` | ❌ | Number of top articles to include in digest | `5` |

### Getting Your Telegram Chat ID

1. Start a chat with your bot on Telegram
2. Send any message to the bot
3. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find `"chat":{"id": YOUR_CHAT_ID}` in the response

---

## 📖 Usage

### One-Time Run (Dry Run)

Preview the curated digest without sending it:

```bash
python fetch.py --dry-run
```

### One-Time Run (Live)

Fetch, score, and send the digest to Telegram:

```bash
python fetch.py
```

### Daily Scheduler

Start the scheduler to run the pipeline automatically every day:

```bash
python main.py
# Logs: "Jal News scheduler started — next run at 07:00 daily"
# Press Ctrl+C to stop
```

### Example Output

The Telegram message includes:
- 🏥 Header with date
- Top 5 articles with AI-generated summaries
- Relevance scores (1–10)
- Source attribution and clickable links
- Clean formatting with emojis

---

## 📁 Project Structure

```
jal-news/
├── fetch.py                    # CLI entry point (one-time run)
├── main.py                     # Scheduler entry point (daily runs)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
│
└── src/
    ├── __init__.py
    ├── container.py            # DI container — wires everything together
    │
    ├── config/                 # Configuration management
    │   ├── __init__.py
    │   └── config.py           # Settings dataclass (from env vars)
    │
    ├── core/                   # Domain models & interfaces (no dependencies)
    │   ├── __init__.py
    │   ├── models.py           # Article, ScoredArticle dataclasses
    │   ├── result.py           # Result types (FetchResult, SendResult)
    │   └── interfaces/         # Abstract base classes
    │       ├── fetcher.py      # IArticleFetcher
    │       ├── scorer.py       # IArticleScorer
    │       ├── sender.py       # IMessageSender
    │       └── formatter.py    # IMessageFormatter
    │
    ├── fetchers/               # News source implementations
    │   ├── base.py             # BaseFetcher with shared logic
    │   ├── rss_fetcher.py      # RSS feed fetcher
    │   ├── newsapi_fetcher.py  # NewsAPI.org fetcher
    │   ├── composite.py        # Aggregates multiple fetchers
    │   └── registry.py         # Fetcher discovery & registration
    │
    ├── scorers/                # AI scoring implementations
    │   ├── base.py             # BaseScorer with shared logic
    │   ├── claude_scorer.py    # Claude 3 Haiku scorer
    │   ├── prompt.py           # Scoring prompt templates
    │   └── factory.py          # ScorerFactory
    │
    ├── senders/                # Message delivery implementations
    │   ├── base.py             # BaseSender with shared logic
    │   ├── telegram_sender.py  # Telegram Bot API sender
    │   └── factory.py          # SenderFactory
    │
    ├── formatters/             # Message formatting implementations
    │   ├── base.py             # BaseFormatter
    │   └── telegram_formatter.py  # Telegram Markdown formatter
    │
    ├── pipeline/               # Pipeline orchestration
    │   ├── pipeline.py         # NewsPipeline (fetch → score → send)
    │   └── builder.py          # PipelineBuilder (fluent interface)
    │
    └── utils/                  # Shared utilities
        └── __init__.py         # Logging setup
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Core language |
| **feedparser** | RSS/Atom feed parsing |
| **requests** | HTTP client for APIs |
| **anthropic** | Anthropic Claude API client |
| **python-dotenv** | Environment variable management |
| **schedule** | Lightweight job scheduling |
| **python-dateutil** | Date parsing from various feed formats |

---

## 🔌 Extensibility

The SOLID architecture makes it easy to extend Jal News:

### Add a New News Source

Create a new fetcher class implementing `IArticleFetcher`:

```python
# src/fetchers/my_fetcher.py
from src.core.interfaces import IArticleFetcher
from src.core.models import Article

class MyCustomFetcher(IArticleFetcher):
    @property
    def name(self) -> str:
        return "My Source"

    def fetch(self) -> list[Article]:
        # Your fetching logic here
        ...
```

### Add a New AI Provider

Create a new scorer implementing `IArticleScorer`:

```python
# src/scorers/openai_scorer.py
from src.core.interfaces import IArticleScorer

class OpenAIScorer(IArticleScorer):
    def score(self, articles, top_n=5):
        # Your scoring logic here
        ...
```

### Add a New Delivery Channel

Create a new sender implementing `IMessageSender`:

```python
# src/senders/email_sender.py
from src.core.interfaces import IMessageSender

class EmailSender(IMessageSender):
    def send(self, articles, dry_run=False):
        # Your sending logic here
        ...
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Guidelines

- Follow existing code patterns and SOLID principles
- Add docstrings to all public classes and methods
- Keep fetchers, scorers, and senders as independent modules
- Use type hints throughout
- Test with `--dry-run` before submitting

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Amaro Labs** — The health & wellness channel this was built for
- **Anthropic** — Claude AI for intelligent article scoring
- **NewsAPI.org** — Additional news aggregation
- RSS feed providers: ScienceDaily, BBC, WHO, Medical Xpress, STAT News, CDC, and more

---

<p align="center">
  Made with ❤️ for <strong>Amaro Labs</strong> — Decoding your everyday health
</p>
