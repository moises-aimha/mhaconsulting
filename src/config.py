import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class GoogleAdsConfig(BaseModel):
    developer_token: str = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "")
    client_id: str = os.getenv("GOOGLE_ADS_CLIENT_ID", "")
    client_secret: str = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "")
    refresh_token: str = os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "")
    login_customer_id: str = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
    customer_id: str = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "")


class AnthropicConfig(BaseModel):
    api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    model: str = "claude-sonnet-4-20250514"


class AppConfig(BaseModel):
    google_ads: GoogleAdsConfig = GoogleAdsConfig()
    anthropic: AnthropicConfig = AnthropicConfig()


config = AppConfig()
