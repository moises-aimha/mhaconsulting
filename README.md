# MHA Consulting — Google Ads + Claude AI Integration

Connects the **Google Ads API** to **Claude (Anthropic)** so you can pull campaign
data and get AI-powered analysis and optimization recommendations.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

You need:

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

Paste the printed refresh token into your `.env` file.

## Usage

### Analyze full account

```bash
python main.py account
python main.py account -q "Which campaigns should I pause?"
```

### Deep-dive into a campaign

```bash
python main.py campaign 123456789
python main.py campaign 123456789 -q "How can I lower CPA?"
```

### Interactive chat

```bash
python main.py chat
```

Loads your account data once, then lets you ask multiple questions in a
back-and-forth conversation with Claude.

## Project structure

```
├── main.py                  # CLI entry point
├── src/
│   ├── config.py            # Loads env vars into typed config
│   ├── google_ads_client.py # Google Ads API queries
│   ├── claude_client.py     # Anthropic / Claude integration
│   └── ads_analyzer.py      # Bridge: pulls data → sends to Claude
├── .env.example             # Template for credentials
└── requirements.txt         # Python dependencies
```
