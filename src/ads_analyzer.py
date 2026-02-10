"""Bridge module — pulls full-funnel data from Google Ads and sends it to Claude for analysis."""

from __future__ import annotations

from src.claude_client import AnalysisMode, analyze, chat
from src.google_ads_client import (
    get_account_summary,
    get_campaigns,
    get_full_campaign_data,
)


def ask_mode() -> AnalysisMode:
    """Prompt the user to select ROAS or Lead Gen mode."""
    print("\nWhat type of account is this?\n")
    print("  1) ROAS-based    (e-commerce / revenue optimization)")
    print("  2) Lead Gen      (lead generation / CPA optimization)")
    print()

    while True:
        choice = input("Select mode (1 or 2): ").strip()
        if choice == "1":
            print("\n→ ROAS mode selected.\n")
            return "roas"
        if choice == "2":
            print("\n→ Lead Gen mode selected.\n")
            return "leadgen"
        print("  Please enter 1 or 2.")


def analyze_account(
    mode: AnalysisMode,
    question: str | None = None,
) -> str:
    """Fetch account-level summary + all campaigns and analyze."""
    print("Fetching account summary and campaigns...")
    summary = get_account_summary()
    campaigns = get_campaigns()
    data = {"account_summary": summary, "campaigns": campaigns}
    print(f"Loaded {len(campaigns)} campaigns. Sending to Claude...\n")
    return analyze(data, mode=mode, user_question=question)


def analyze_campaign(
    campaign_id: str,
    mode: AnalysisMode,
    question: str | None = None,
) -> str:
    """Full-funnel deep-dive: ad groups → ads → keywords → search terms → Claude."""
    print(f"Fetching full funnel for campaign {campaign_id}...")
    data = get_full_campaign_data(campaign_id)
    total = (
        len(data["ad_groups"])
        + len(data["ads"])
        + len(data["keywords"])
        + len(data["search_terms"])
    )
    print(
        f"Loaded {len(data['ad_groups'])} ad groups, "
        f"{len(data['ads'])} ads, "
        f"{len(data['keywords'])} keywords, "
        f"{len(data['search_terms'])} search terms "
        f"({total} total rows). Sending to Claude...\n"
    )
    return analyze(data, mode=mode, user_question=question)


def interactive_session(mode: AnalysisMode) -> None:
    """Run an interactive CLI chat session with full Google Ads context.

    Loads account data once, then lets the user ask multiple questions.
    """
    print("Loading Google Ads data...")
    summary = get_account_summary()
    campaigns = get_campaigns()
    context = {"account_summary": summary, "campaigns": campaigns}
    print(f"Loaded {len(campaigns)} campaigns.")
    mode_label = "ROAS" if mode == "roas" else "Lead Gen"
    print(f"Mode: {mode_label}\n")

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
        response = chat(messages, mode=mode, google_ads_context=context)
        messages.append({"role": "assistant", "content": response})
        print(f"\nClaude: {response}\n")
