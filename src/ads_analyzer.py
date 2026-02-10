"""Bridge module — pulls data from Google Ads and sends it to Claude for analysis."""

from src.google_ads_client import (
    get_account_summary,
    get_campaigns,
    get_ad_groups,
    get_keywords,
)
from src.claude_client import analyze, chat


def analyze_account(question: str | None = None) -> str:
    """Fetch account-level summary and ask Claude to analyze it."""
    summary = get_account_summary()
    campaigns = get_campaigns()
    data = {"account_summary": summary, "campaigns": campaigns}
    return analyze(data, user_question=question)


def analyze_campaign(campaign_id: str, question: str | None = None) -> str:
    """Deep-dive into a single campaign: ad groups + keywords → Claude."""
    ad_groups = get_ad_groups(campaign_id)
    keywords = get_keywords(campaign_id)
    data = {
        "campaign_id": campaign_id,
        "ad_groups": ad_groups,
        "keywords": keywords,
    }
    return analyze(data, user_question=question)


def interactive_session() -> None:
    """Run an interactive CLI chat session with Google Ads context.

    Loads account data once, then lets the user ask multiple questions.
    """
    print("Loading Google Ads data...")
    summary = get_account_summary()
    campaigns = get_campaigns()
    context = {"account_summary": summary, "campaigns": campaigns}
    print(f"Loaded {len(campaigns)} campaigns.\n")

    messages: list[dict] = []
    print("Ask questions about your Google Ads account. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        response = chat(messages, google_ads_context=context)
        messages.append({"role": "assistant", "content": response})
        print(f"\nClaude: {response}\n")
