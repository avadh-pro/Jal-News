"""Scoring prompt template for Claude 3.5 Haiku."""

SYSTEM_PROMPT = """You are an expert health news curator for **Amaro Labs** — a physiotherapist's \
health & wellness channel ("Decoding your everyday health"). The audience wants shareable, \
surprising health discoveries they can discuss with friends and family.

Your job is to score each article on four criteria (1-10) and write a short WhatsApp-friendly summary."""

SCORING_PROMPT_TEMPLATE = """\
Score each article below on these criteria (1-10 scale):

1. **Shareability**: How likely is someone to share this on social media? \
("OMG did you see this?" factor)
2. **Novelty**: Is this genuinely new research or a breakthrough, vs. rehashed/incremental news?
3. **Relevance**: How relevant is this to everyday health & wellness for a general audience? \
Bonus for physiotherapy/movement/pain science angle.
4. **Viral potential**: Catchy headline? Surprising finding? Counterintuitive result? \
Could this become a trending topic?

Also generate a 1-2 sentence summary suitable for WhatsApp — concise, engaging, \
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
    "summary": "🧠 New study finds 10 min of daily walking cuts dementia risk by 50%! Researchers say it's never too late to start."
  }}
]
```

Rules:
- "index" must match the article's position (0-based) in the list above.
- All scores must be integers from 1 to 10.
- Summary must be 1-2 sentences, max 200 characters, include 1-2 relevant emojis.
- Return one entry per article, in order.
- Output ONLY the JSON array — no markdown fences, no extra text."""


def build_articles_text(articles: list[dict]) -> str:
    """Format a batch of articles into numbered text for the prompt.

    Args:
        articles: List of dicts with keys: index, title, description, source_name.

    Returns:
        Formatted string with one article per block.
    """
    parts: list[str] = []
    for a in articles:
        parts.append(
            f"[{a['index']}] {a['title']}\n"
            f"    Source: {a['source_name']}\n"
            f"    Description: {a['description']}"
        )
    return "\n\n".join(parts)


def build_scoring_prompt(articles: list[dict]) -> str:
    """Build the complete scoring prompt for a batch of articles.

    Args:
        articles: List of dicts with keys: index, title, description, source_name.

    Returns:
        The formatted prompt string ready to send to Claude.
    """
    articles_text = build_articles_text(articles)
    return SCORING_PROMPT_TEMPLATE.format(articles_text=articles_text)

