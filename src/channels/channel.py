"""Channel dataclass — bundles all topic-specific configuration."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Channel:
    """A news channel defines a topic-specific pipeline configuration.

    Each channel specifies its own RSS feeds, NewsAPI query, scorer prompt,
    and formatter branding so the same pipeline can serve any topic.

    Feed entries support optional credibility metadata:
        feeds:
          - name: "OpenAI Blog"
            url: "https://openai.com/news/rss.xml"
            tier: "primary"
            weight: 1.0

    Tier values: "primary" (lab blogs, official sources), "expert" (domain
    experts, analysts), "major-outlet" (established journalism), "niche"
    (specialized trade publications), "community" (HN, Dev.to, Reddit),
    "aggregator" (rewrites, general tech). Default: "general".

    Weight values: 0.0-1.0 multiplier on the composite score. Default: 1.0.
    """

    slug: str
    name: str
    feeds: list[dict] = field(default_factory=list)
    newsapi_query: str = ""
    newsapi_domains: str = ""
    scoring_system_prompt: str = ""
    scoring_relevance_hint: str = ""
    header_emoji: str = "📰"
    category_emojis: list[str] = field(
        default_factory=lambda: ["📰", "🔍", "💡", "⚡", "🌐"]
    )
    footer_text: str = "Curated by AI"
    telegram_chat_id: str = ""
    schedule_time: str = ""
    top_n: int = 5
