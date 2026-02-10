"""Anthropic (Claude) client — sends Google Ads data to Claude for analysis."""

import json
import anthropic

from src.config import config

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=config.anthropic.api_key)
    return _client


SYSTEM_PROMPT = """\
You are a senior Google Ads strategist and data analyst.
You receive structured Google Ads performance data (JSON) and provide:
  • Clear, actionable insights
  • Specific optimization recommendations with expected impact
  • Budget reallocation suggestions when relevant
  • Keyword and ad-copy improvement ideas
Keep answers concise and data-driven. Use numbers from the data to support every claim.
"""


def analyze(data: dict | list, user_question: str | None = None) -> str:
    """Send Google Ads data to Claude and return the analysis text.

    Args:
        data: The Google Ads data (campaigns, keywords, etc.) as a dict/list.
        user_question: Optional follow-up question to ask about the data.

    Returns:
        Claude's analysis as a plain-text string.
    """
    client = _get_client()

    user_content = f"Here is the Google Ads performance data:\n\n```json\n{json.dumps(data, indent=2)}\n```"
    if user_question:
        user_content += f"\n\nAdditional question: {user_question}"
    else:
        user_content += "\n\nProvide a full performance analysis with optimization recommendations."

    message = client.messages.create(
        model=config.anthropic.model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text


def chat(messages: list[dict], google_ads_context: dict | list | None = None) -> str:
    """Multi-turn conversation with optional Google Ads context.

    Args:
        messages: List of {"role": "user"|"assistant", "content": "..."} dicts.
        google_ads_context: Optional data to include as context at the start.

    Returns:
        Claude's response text.
    """
    client = _get_client()

    system = SYSTEM_PROMPT
    if google_ads_context:
        system += (
            f"\n\nCurrent Google Ads data for reference:\n"
            f"```json\n{json.dumps(google_ads_context, indent=2)}\n```"
        )

    message = client.messages.create(
        model=config.anthropic.model,
        max_tokens=4096,
        system=system,
        messages=messages,
    )
    return message.content[0].text
