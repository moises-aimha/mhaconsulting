# MHA Consulting — Google Ads + Claude AI Integration

Connects the **Google Ads API** to **Claude (Anthropic)** so you can pull
full-funnel campaign data and get AI-powered analysis and optimization
recommendations.

Supports two analysis modes:
- **ROAS mode** — e-commerce / revenue-focused (optimizes return on ad spend)
- **Lead Gen mode** — lead generation / CPA-focused (optimizes cost per lead)

## Data coverage (full funnel)

| Level | What's fetched |
|---|---|
| Account | Impressions, clicks, cost, conversions, conversion value, ROAS, CTR |
| Campaigns | All campaigns with metrics, channel type, ROAS |
| Ad Groups | Per-campaign ad groups with cost, conversions, ROAS |
| Ads | Individual ads with headlines, descriptions, final URLs, performance |
| Keywords | Keyword text, match type, CPC, conversions, ROAS |
| Search Terms | Actual search queries triggering your ads, with performance data |

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Fill in:

| Variable | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads API Center → API Access |
| `GOOGLE_ADS_CLIENT_ID` | Google Cloud Console → OAuth 2.0 credentials |
| `GOOGLE_ADS_CLIENT_SECRET` | Same as above |
| `GOOGLE_ADS_REFRESH_TOKEN` | Generated via OAuth flow (see below) |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Your MCC account ID (no dashes) |
| `GOOGLE_ADS_CUSTOMER_ID` | The account you want to query (no dashes) |

### 3. Generate a Google Ads refresh token

```bash
pip install google-auth-oauthlib
python -c "
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_config(
    {'installed': {
        'client_id': 'YOUR_CLIENT_ID',
        'client_secret': 'YOUR_CLIENT_SECRET',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
    }},
    scopes=['https://www.googleapis.com/auth/adwords'],
)
flow.run_local_server(port=8080)
print('Refresh token:', flow.credentials.refresh_token)
"
```

## Usage

Every command first asks: **ROAS-based or Lead Gen?** (or pass `--mode`/`-m` to skip the prompt).

### Analyze full account

```bash
python main.py account
python main.py -m roas account -q "Which campaigns should I pause?"
python main.py -m leadgen account -q "Where are my cheapest leads coming from?"
```

### Full-funnel campaign deep-dive

Fetches ad groups, ads, keywords, and search terms for one campaign:

```bash
python main.py campaign 123456789
python main.py -m roas campaign 123456789 -q "What search terms are wasting budget?"
python main.py -m leadgen campaign 123456789 -q "Which ad copy drives the most leads?"
```

### Interactive chat

```bash
python main.py chat
```

Loads account data once, then lets you ask multiple follow-up questions in a
conversation with Claude.

## Project structure

```
├── main.py                  # CLI entry point (mode selection + subcommands)
├── CLAUDE.md                # Context file for Claude Code sessions
├── src/
│   ├── config.py            # Loads env vars into typed Pydantic config
│   ├── google_ads_client.py # Google Ads API: campaigns, ad groups, ads, keywords, search terms
│   ├── claude_client.py     # Anthropic SDK: ROAS + Lead Gen system prompts
│   └── ads_analyzer.py      # Bridge: pulls full-funnel data → sends to Claude
├── .env.example             # Template for credentials
└── requirements.txt         # Python dependencies
```
