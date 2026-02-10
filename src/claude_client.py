"""Anthropic (Claude) client — sends Google Ads data to Claude for analysis.

Supports two analysis modes:
  - ROAS: e-commerce / revenue-focused optimization
  - Lead Gen: lead generation / CPA-focused optimization
"""

import json
from typing import Literal

import anthropic

from src.config import config

AnalysisMode = Literal["roas", "leadgen"]

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=config.anthropic.api_key)
    return _client


# ── System prompts per mode ──────────────────────────────────────────────────

SYSTEM_PROMPT_ROAS = """\
You are a senior Google Ads strategist specializing in e-commerce and ROAS optimization.
You receive structured Google Ads performance data (JSON) spanning the full funnel:
campaigns, ad groups, ads, keywords, and search terms.

Your analysis must focus on:
  • ROAS (Return on Ad Spend) at every level — flag anything below target
  • Revenue-driving keywords and search terms vs. wasted spend
  • Product/ad-group level profitability — which ad groups and ads generate the most revenue per dollar
  • Shopping/PMax campaign structure improvements when applicable
  • Bid strategy recommendations (target ROAS, maximize conversion value)
  • Budget reallocation from low-ROAS to high-ROAS segments
  • Ad copy and headline testing ideas to improve conversion rates
  • Negative keyword opportunities from the search term report (terms with spend but no revenue)

Key metrics to prioritize: ROAS, conversion value, cost, cost per conversion, conversion rate.
Always reference specific numbers from the data. Be concise and actionable.
"""

SYSTEM_PROMPT_LEADGEN = """\
You are a senior Google Ads strategist specializing in lead generation campaigns.
You receive structured Google Ads performance data (JSON) spanning the full funnel:
campaigns, ad groups, ads, keywords, and search terms.

Your analysis must focus on:
  • Cost per lead (CPL / cost per conversion) at every level — flag anything above target
  • Lead volume vs. cost efficiency tradeoffs
  • Which keywords and search terms drive the most leads at the lowest cost
  • Ad group structure — are leads concentrated or spread across groups?
  • Ad copy performance — which headlines and descriptions convert best for lead gen
  • Landing page URL analysis — are different final URLs performing differently?
  • Bid strategy recommendations (target CPA, maximize conversions)
  • Budget reallocation from high-CPL to low-CPL segments
  • Negative keyword opportunities from the search term report (terms with spend but no leads)
  • Geographic, device, or schedule patterns if visible in the data

Key metrics to prioritize: conversions (leads), cost per conversion (CPL), CTR, conversion rate.
Always reference specific numbers from the data. Be concise and actionable.
"""

SYSTEM_PROMPTS: dict[AnalysisMode, str] = {
    "roas": SYSTEM_PROMPT_ROAS,
    "leadgen": SYSTEM_PROMPT_LEADGEN,
}


def _get_system_prompt(mode: AnalysisMode) -> str:
    return SYSTEM_PROMPTS[mode]


# ── Public API ───────────────────────────────────────────────────────────────


def analyze(
    data: dict | list,
    mode: AnalysisMode = "roas",
    user_question: str | None = None,
) -> str:
    """Send Google Ads data to Claude and return the analysis text.

    Args:
        data: The Google Ads data (campaigns, keywords, etc.) as a dict/list.
        mode: Analysis mode — "roas" or "leadgen".
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
        system=_get_system_prompt(mode),
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text


def chat(
    messages: list[dict],
    mode: AnalysisMode = "roas",
    google_ads_context: dict | list | None = None,
) -> str:
    """Multi-turn conversation with optional Google Ads context.

    Args:
        messages: List of {"role": "user"|"assistant", "content": "..."} dicts.
        mode: Analysis mode — "roas" or "leadgen".
        google_ads_context: Optional data to include as context at the start.

    Returns:
        Claude's response text.
    """
    client = _get_client()

    system = _get_system_prompt(mode)
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
