#!/usr/bin/env python3
"""Standalone script — fetch raw Google Ads data and display it in the terminal.

Usage:
    python raw_report.py                     # Account overview + all campaigns
    python raw_report.py <campaign_id>       # Full funnel for one campaign
"""

from __future__ import annotations

import sys

from src.google_ads_client import (
    get_account_summary,
    get_campaigns,
    get_full_campaign_data,
)


# ── Formatting helpers ───────────────────────────────────────────────────────

DOLLAR_FIELDS = {"cost", "avg_cpc", "cost_per_conversion", "conversion_value"}
SEPARATOR = "=" * 70


def _header(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def _print_dict(data: dict) -> None:
    """Print a key-value dict (account summary)."""
    for key, value in data.items():
        if isinstance(value, float):
            if key in DOLLAR_FIELDS:
                formatted = f"${value:,.2f}"
            else:
                formatted = f"{value:,.4f}"
        else:
            formatted = str(value)
        print(f"  {key:<28} {formatted}")


def _print_table(rows: list[dict]) -> None:
    """Print a list of dicts as a formatted table."""
    if not rows:
        print("  (no data)")
        return

    keys = list(rows[0].keys())

    # Calculate column widths: max of header length or longest value
    widths: dict[str, int] = {}
    for key in keys:
        max_val_len = max(
            len(_format_cell(key, row[key])) for row in rows
        )
        widths[key] = max(len(key), min(max_val_len, 30))

    # Header
    header = " | ".join(f"{k:<{widths[k]}}" for k in keys)
    print(f"  {header}")
    print(f"  {'-' * len(header)}")

    # Rows
    for row in rows:
        cells = []
        for key in keys:
            cell = _format_cell(key, row[key])
            cells.append(f"{cell:<{widths[key]}}")
        print(f"  {' | '.join(cells)}")


def _format_cell(key: str, value) -> str:
    """Format a single cell value for display."""
    if isinstance(value, float):
        if key in DOLLAR_FIELDS:
            return f"${value:,.2f}"
        return f"{value:,.2f}"
    if isinstance(value, list):
        text = "; ".join(str(x) for x in value[:3])
        if len(value) > 3:
            text += "..."
        return text
    return str(value)


# ── Report functions ─────────────────────────────────────────────────────────


def report_account() -> None:
    """Fetch and display account summary + all campaigns."""
    print("\n  Fetching account data...\n")

    summary = get_account_summary()
    campaigns = get_campaigns()

    _header("ACCOUNT SUMMARY (Last 30 Days)")
    if summary:
        _print_dict(summary)
    else:
        print("  (no data)")

    _header(f"ALL CAMPAIGNS ({len(campaigns)})")
    _print_table(campaigns)

    print(f"\n{SEPARATOR}")
    print(f"  Done — {len(campaigns)} campaigns loaded.")
    print(SEPARATOR)


def report_campaign(campaign_id: str) -> None:
    """Fetch and display full funnel for a single campaign."""
    print(f"\n  Fetching full funnel for campaign {campaign_id}...\n")

    data = get_full_campaign_data(campaign_id)

    ad_groups = data["ad_groups"]
    ads = data["ads"]
    keywords = data["keywords"]
    search_terms = data["search_terms"]

    _header(f"AD GROUPS ({len(ad_groups)})")
    _print_table(ad_groups)

    _header(f"ADS ({len(ads)})")
    _print_table(ads)

    _header(f"KEYWORDS ({len(keywords)})")
    _print_table(keywords)

    _header(f"SEARCH TERMS ({len(search_terms)})")
    _print_table(search_terms)

    total = len(ad_groups) + len(ads) + len(keywords) + len(search_terms)
    print(f"\n{SEPARATOR}")
    print(f"  Done — Campaign {campaign_id}")
    print(f"  {len(ad_groups)} ad groups | {len(ads)} ads | {len(keywords)} keywords | {len(search_terms)} search terms")
    print(f"  {total} total rows fetched.")
    print(SEPARATOR)


# ── Entry point ──────────────────────────────────────────────────────────────


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] not in ("-h", "--help"):
        campaign_id = sys.argv[1]
        report_campaign(campaign_id)
    else:
        if len(sys.argv) > 1:
            print("Usage:")
            print("  python raw_report.py                  # Account overview")
            print("  python raw_report.py <campaign_id>    # Full campaign funnel")
            return
        report_account()


if __name__ == "__main__":
    main()
