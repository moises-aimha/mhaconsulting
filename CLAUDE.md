# CLAUDE.md — Project context for Claude Code

## What this project does

This is a **Google Ads + Claude AI integration** for MHA Consulting. It pulls
performance data from the Google Ads API (campaigns, ad groups, ads, keywords,
search terms) and sends it to Claude for AI-powered analysis and optimization
recommendations.

The tool supports two analysis modes:
- **ROAS mode** — for e-commerce / revenue-focused accounts (optimizes return on ad spend)
- **Lead Gen mode** — for lead generation accounts (optimizes cost per lead, conversion volume)

## Project structure

```
├── main.py                  # CLI entry point — mode selection + subcommands
├── src/
│   ├── config.py            # Loads .env into typed Pydantic config
│   ├── google_ads_client.py # Google Ads API queries (GAQL)
│   ├── claude_client.py     # Anthropic SDK — prompts, analyze, chat
│   └── ads_analyzer.py      # Bridge: pulls Ads data → sends to Claude
├── .env.example             # Template for API credentials
├── requirements.txt         # Python deps: google-ads, anthropic, pydantic, python-dotenv
└── README.md
```

## Key conventions

- All Google Ads queries use **GAQL** (Google Ads Query Language)
- Monetary values from the API come in **micros** (÷ 1,000,000 for dollars)
- The `config.py` module is the single source of truth for all credentials
- Claude system prompts live in `claude_client.py` — one per analysis mode
- Never commit `.env` or any file containing real credentials

## How to run

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in credentials
python main.py account
python main.py campaign <id>
python main.py chat
```

## When making changes

- Keep Google Ads queries in `google_ads_client.py` — one function per entity type
- Keep Claude prompt logic in `claude_client.py` — do not scatter prompts across files
- The bridge logic in `ads_analyzer.py` should only orchestrate (fetch → analyze)
- Use type hints everywhere; the project targets Python 3.11+
- Keep functions small and focused — one query per function in the Ads client
