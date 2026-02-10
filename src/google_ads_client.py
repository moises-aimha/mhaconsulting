"""Google Ads API client — fetches campaign, ad group, and keyword data."""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from src.config import config


def _build_client() -> GoogleAdsClient:
    """Build an authenticated GoogleAdsClient from environment config."""
    credentials = {
        "developer_token": config.google_ads.developer_token,
        "client_id": config.google_ads.client_id,
        "client_secret": config.google_ads.client_secret,
        "refresh_token": config.google_ads.refresh_token,
        "login_customer_id": config.google_ads.login_customer_id,
        "use_proto_plus": True,
    }
    return GoogleAdsClient.load_from_dict(credentials)


def _query(ga_service, customer_id: str, query: str) -> list[dict]:
    """Run a GAQL query and return rows as dicts."""
    rows = []
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            rows.append(row)
    except GoogleAdsException as ex:
        for error in ex.failure.errors:
            raise RuntimeError(
                f"Google Ads API error: [{error.error_code}] {error.message}"
            ) from ex
    return rows


# ── Public helpers ───────────────────────────────────────────────────────────


def get_campaigns(customer_id: str | None = None) -> list[dict]:
    """Return all campaigns with core metrics for the last 30 days."""
    cid = customer_id or config.google_ads.customer_id
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.cost_per_conversion
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
    """
    rows = _query(ga_service, cid, query)
    return [
        {
            "id": str(r.campaign.id),
            "name": r.campaign.name,
            "status": r.campaign.status.name,
            "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks,
            "cost": r.metrics.cost_micros / 1_000_000,
            "conversions": r.metrics.conversions,
            "cost_per_conversion": r.metrics.cost_per_conversion / 1_000_000,
        }
        for r in rows
    ]


def get_ad_groups(campaign_id: str, customer_id: str | None = None) -> list[dict]:
    """Return ad groups for a given campaign with metrics."""
    cid = customer_id or config.google_ads.customer_id
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            ad_group.id,
            ad_group.name,
            ad_group.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM ad_group
        WHERE campaign.id = {campaign_id}
          AND segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
    """
    rows = _query(ga_service, cid, query)
    return [
        {
            "id": str(r.ad_group.id),
            "name": r.ad_group.name,
            "status": r.ad_group.status.name,
            "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks,
            "cost": r.metrics.cost_micros / 1_000_000,
            "conversions": r.metrics.conversions,
        }
        for r in rows
    ]


def get_keywords(campaign_id: str, customer_id: str | None = None) -> list[dict]:
    """Return keyword performance for a campaign."""
    cid = customer_id or config.google_ads.customer_id
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.average_cpc
        FROM keyword_view
        WHERE campaign.id = {campaign_id}
          AND segments.date DURING LAST_30_DAYS
        ORDER BY metrics.impressions DESC
        LIMIT 50
    """
    rows = _query(ga_service, cid, query)
    return [
        {
            "keyword": r.ad_group_criterion.keyword.text,
            "match_type": r.ad_group_criterion.keyword.match_type.name,
            "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks,
            "cost": r.metrics.cost_micros / 1_000_000,
            "conversions": r.metrics.conversions,
            "avg_cpc": r.metrics.average_cpc / 1_000_000,
        }
        for r in rows
    ]


def get_account_summary(customer_id: str | None = None) -> dict:
    """Return a high-level account summary for the last 30 days."""
    cid = customer_id or config.google_ads.customer_id
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.cost_per_conversion,
            metrics.clicks / metrics.impressions AS ctr
        FROM customer
        WHERE segments.date DURING LAST_30_DAYS
    """
    rows = _query(ga_service, cid, query)
    if not rows:
        return {}
    r = rows[0]
    return {
        "impressions": r.metrics.impressions,
        "clicks": r.metrics.clicks,
        "cost": r.metrics.cost_micros / 1_000_000,
        "conversions": r.metrics.conversions,
        "cost_per_conversion": r.metrics.cost_per_conversion / 1_000_000,
        "ctr": r.metrics.clicks / r.metrics.impressions if r.metrics.impressions else 0,
    }
