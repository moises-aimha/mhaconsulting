#!/usr/bin/env python3
"""Entry point — run different analysis modes from the CLI.

Every command starts by asking whether the account is ROAS-based or Lead Gen-based,
then fetches the appropriate data and sends it to Claude with the right prompt.
"""

import argparse
import sys

from src.ads_analyzer import (
    analyze_account,
    analyze_campaign,
    ask_mode,
    interactive_session,
)


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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

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
