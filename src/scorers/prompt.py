"""Scoring prompt templates — channel-aware with credibility dimension."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.channels.channel import Channel

_DEFAULT_SYSTEM_PROMPT = (
    "You are an expert news curator. Your job is to score each article "
    "on five criteria (1-10) and write a short summary."
)

SCORING_PROMPT_TEMPLATE = """\
Score each article below on these criteria (1-10 scale):

1. **Shareability**: How likely is someone to share this on social media? \
("OMG did you see this?" factor)
2. **Novelty**: Is this genuinely new research or a breakthrough, vs. rehashed/incremental news?
3. **Relevance**: {relevance_hint}
4. **Viral potential**: Catchy headline? Surprising finding? Counterintuitive result? \
Could this become a trending topic?
5. **Source credibility**: How established and trustworthy is this source for this topic? \
Primary sources (official lab announcements, peer-reviewed research, original reporting) \
score highest. Rewrites, aggregations, and clickbait score lowest. \
Consider the source tier provided with each article.

Also generate a 1-2 sentence summary suitable for messaging — concise, engaging, \
emoji-friendly, written so the reader immediately wants to tap the link.

---

ARTICLES:

{articles_text}

---

Respond with ONLY a valid JSON array. Each element must have this exact structure:
```json
[
  {{
    "index": 0,
    "shareability": 8,
    "novelty": 7,
    "relevance": 9,
    "viral_potential": 6,
    "source_credibility": 8,
    "summary": "🔥 Short engaging summary here."
  }}
]
```

Rules:
- "index" must match the article's position (0-based) in the list above.
- All scores must be integers from 1 to 10.
- Summary must be 1-2 sentences, max 200 characters, include 1-2 relevant emojis.
- Return one entry per article, in order.
- Output ONLY the JSON array — no markdown fences, no extra text."""


def build_system_prompt(channel: Channel | None = None) -> str:
    """Build the system prompt from a channel config."""
    if channel and channel.scoring_system_prompt:
        base = channel.scoring_system_prompt
    else:
        base = _DEFAULT_SYSTEM_PROMPT

    return (
        f"{base}\n\n"
        "Your job is to score each article on five criteria (1-10) "
        "and write a short summary. Prioritize primary sources and original "
        "reporting over rewrites and aggregations."
    )


def build_articles_text(articles: list[dict]) -> str:
    """Format a batch of articles into numbered text for the prompt.

    Args:
        articles: List of dicts with keys: index, title, description,
            source_name, source_tier, coverage_count.

    Returns:
        Formatted string with one article per block.
    """
    parts: list[str] = []
    for a in articles:
        tier = a.get("source_tier", "general")
        coverage = a.get("coverage_count", 1)

        block = (
            f"[{a['index']}] {a['title']}\n"
            f"    Source: {a['source_name']} (tier: {tier})\n"
            f"    Description: {a['description']}"
        )
        if coverage > 1:
            block += f"\n    Coverage: reported by {coverage} sources"

        parts.append(block)
    return "\n\n".join(parts)


def build_scoring_prompt(
    articles: list[dict],
    channel: Channel | None = None,
) -> str:
    """Build the complete scoring prompt for a batch of articles."""
    articles_text = build_articles_text(articles)

    if channel and channel.scoring_relevance_hint:
        relevance_hint = channel.scoring_relevance_hint
    else:
        relevance_hint = (
            "How relevant and interesting is this to the target audience?"
        )

    return SCORING_PROMPT_TEMPLATE.format(
        articles_text=articles_text,
        relevance_hint=relevance_hint,
    )
