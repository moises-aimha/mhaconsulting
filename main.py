#!/usr/bin/env python3
"""Entry point — run different analysis modes from the CLI.

Every command starts by asking whether the account is ROAS-based or Lead Gen-based,
then fetches the appropriate data and sends it to Claude with the right prompt.
"""

from __future__ import annotations

import argparse
import sys

from src.ads_analyzer import (
    analyze_account,
    analyze_campaign,
    ask_mode,
    interactive_session,
)
from src.google_ads_client import (
    get_account_summary,
    get_campaigns,
    get_full_campaign_data,
)


def _section(title: str, data: list[dict] | dict) -> None:
    """Print a labeled section of data."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
    if isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k:<25} {v}")
    elif isinstance(data, list):
        if not data:
            print("  (no data)")
            return
        # Print as a table: header row + data rows
        keys = list(data[0].keys())
        print("  " + " | ".join(f"{k:<18}" for k in keys))
        print("  " + "-" * (21 * len(keys)))
        for row in data:
            vals = []
            for k in keys:
                v = row[k]
                if isinstance(v, float):
                    vals.append(f"${v:,.2f}" if k in ("cost", "avg_cpc", "cost_per_conversion", "conversion_value") else f"{v:,.2f}")
                elif isinstance(v, list):
                    vals.append("; ".join(str(x) for x in v[:3]) + ("..." if len(v) > 3 else ""))
                else:
                    vals.append(str(v))
            print("  " + " | ".join(f"{v:<18}" for v in vals))
    print()


def _print_raw(campaign_id: str | None) -> None:
    """Fetch raw Google Ads data and display it in the terminal."""
    if campaign_id:
        print(f"\nFetching full funnel for campaign {campaign_id}...")
        data = get_full_campaign_data(campaign_id)
        _section(f"AD GROUPS — Campaign {campaign_id}", data["ad_groups"])
        _section(f"ADS — Campaign {campaign_id}", data["ads"])
        _section(f"KEYWORDS — Campaign {campaign_id}", data["keywords"])
        _section(f"SEARCH TERMS — Campaign {campaign_id}", data["search_terms"])
    else:
        print("\nFetching account overview...")
        summary = get_account_summary()
        campaigns = get_campaigns()
        _section("ACCOUNT SUMMARY", summary)
        _section("CAMPAIGNS", campaigns)

    print("Done.\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Google Ads data with Claude AI"
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["roas", "leadgen"],
        help="Analysis mode: roas (e-commerce) or leadgen (lead generation). "
        "If not provided, you will be prompted.",
    )
    sub = parser.add_subparsers(dest="command")

    # ── account ──────────────────────────────────────────────────────────
    acct = sub.add_parser("account", help="Analyze the full account")
    acct.add_argument("-q", "--question", help="Specific question to ask Claude")

    # ── campaign ─────────────────────────────────────────────────────────
    camp = sub.add_parser(
        "campaign", help="Full-funnel deep-dive into one campaign"
    )
    camp.add_argument("campaign_id", help="Google Ads campaign ID")
    camp.add_argument("-q", "--question", help="Specific question to ask Claude")

    # ── chat ─────────────────────────────────────────────────────────────
    sub.add_parser("chat", help="Interactive chat session with Google Ads context")

    # ── raw ──────────────────────────────────────────────────────────────
    raw = sub.add_parser(
        "raw", help="Fetch and display raw Google Ads data (no Claude analysis)"
    )
    raw.add_argument(
        "campaign_id",
        nargs="?",
        default=None,
        help="Campaign ID for full-funnel data. Omit for account-level overview.",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # ── raw: no mode needed ──────────────────────────────────────────────
    if args.command == "raw":
        _print_raw(args.campaign_id)
        return

    # Determine analysis mode (prompt if not passed via --mode)
    mode = args.mode if args.mode else ask_mode()

    if args.command == "account":
        print(analyze_account(mode=mode, question=args.question))
    elif args.command == "campaign":
        print(analyze_campaign(args.campaign_id, mode=mode, question=args.question))
    elif args.command == "chat":
        interactive_session(mode=mode)


if __name__ == "__main__":
    main()
