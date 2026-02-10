#!/usr/bin/env python3
"""Entry point — run different analysis modes from the CLI."""

import argparse
import sys

from src.ads_analyzer import analyze_account, analyze_campaign, interactive_session


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Google Ads data with Claude AI"
    )
    sub = parser.add_subparsers(dest="command")

    # ── account ──────────────────────────────────────────────────────────
    acct = sub.add_parser("account", help="Analyze the full account")
    acct.add_argument("-q", "--question", help="Specific question to ask Claude")

    # ── campaign ─────────────────────────────────────────────────────────
    camp = sub.add_parser("campaign", help="Deep-dive into one campaign")
    camp.add_argument("campaign_id", help="Google Ads campaign ID")
    camp.add_argument("-q", "--question", help="Specific question to ask Claude")

    # ── chat ─────────────────────────────────────────────────────────────
    sub.add_parser("chat", help="Interactive chat session with Google Ads context")

    args = parser.parse_args()

    if args.command == "account":
        print(analyze_account(question=args.question))
    elif args.command == "campaign":
        print(analyze_campaign(args.campaign_id, question=args.question))
    elif args.command == "chat":
        interactive_session()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
