"""Google Ads API client — fetches the full funnel: campaigns → ad groups → ads → keywords → search terms."""

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


def _query(ga_service, customer_id: str, query: str) -> list:
    """Run a GAQL query and return rows."""
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


# ── Account ──────────────────────────────────────────────────────────────────


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
            metrics.conversions_value,
            metrics.cost_per_conversion
        FROM customer
        WHERE segments.date DURING LAST_30_DAYS
    """
    rows = _query(ga_service, cid, query)
    if not rows:
        return {}
    r = rows[0]
    cost = r.metrics.cost_micros / 1_000_000
    conv_value = r.metrics.conversions_value
    return {
        "impressions": r.metrics.impressions,
        "clicks": r.metrics.clicks,
        "cost": cost,
        "conversions": r.metrics.conversions,
        "conversion_value": conv_value,
        "cost_per_conversion": r.metrics.cost_per_conversion / 1_000_000,
        "roas": conv_value / cost if cost else 0,
        "ctr": r.metrics.clicks / r.metrics.impressions if r.metrics.impressions else 0,
    }


# ── Campaigns ────────────────────────────────────────────────────────────────


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
            campaign.advertising_channel_type,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.cost_per_conversion
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
    """
    rows = _query(ga_service, cid, query)
    results = []
    for r in rows:
        cost = r.metrics.cost_micros / 1_000_000
        conv_value = r.metrics.conversions_value
        results.append({
            "id": str(r.campaign.id),
            "name": r.campaign.name,
            "status": r.campaign.status.name,
            "channel_type": r.campaign.advertising_channel_type.name,
            "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks,
            "cost": cost,
            "conversions": r.metrics.conversions,
            "conversion_value": conv_value,
            "cost_per_conversion": r.metrics.cost_per_conversion / 1_000_000,
            "roas": conv_value / cost if cost else 0,
        })
    return results


# ── Ad Groups ────────────────────────────────────────────────────────────────


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
            metrics.conversions,
            metrics.conversions_value,
            metrics.cost_per_conversion
        FROM ad_group
        WHERE campaign.id = {campaign_id}
          AND segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
    """
    rows = _query(ga_service, cid, query)
    results = []
    for r in rows:
        cost = r.metrics.cost_micros / 1_000_000
        conv_value = r.metrics.conversions_value
        results.append({
            "id": str(r.ad_group.id),
            "name": r.ad_group.name,
            "status": r.ad_group.status.name,
            "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks,
            "cost": cost,
            "conversions": r.metrics.conversions,
            "conversion_value": conv_value,
            "cost_per_conversion": r.metrics.cost_per_conversion / 1_000_000,
            "roas": conv_value / cost if cost else 0,
        })
    return results


# ── Ads ──────────────────────────────────────────────────────────────────────


def get_ads(campaign_id: str, customer_id: str | None = None) -> list[dict]:
    """Return ad-level performance for a campaign."""
    cid = customer_id or config.google_ads.customer_id
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            ad_group_ad.ad.id,
            ad_group_ad.ad.name,
            ad_group_ad.ad.type,
            ad_group_ad.ad.final_urls,
            ad_group_ad.ad.responsive_search_ad.headlines,
            ad_group_ad.ad.responsive_search_ad.descriptions,
            ad_group_ad.status,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.cost_per_conversion
        FROM ad_group_ad
        WHERE campaign.id = {campaign_id}
          AND segments.date DURING LAST_30_DAYS
        ORDER BY metrics.impressions DESC
        LIMIT 50
    """
    rows = _query(ga_service, cid, query)
    results = []
    for r in rows:
        cost = r.metrics.cost_micros / 1_000_000
        conv_value = r.metrics.conversions_value

        # Extract headline/description text from responsive search ads
        headlines = []
        descriptions = []
        if r.ad_group_ad.ad.responsive_search_ad:
            headlines = [h.text for h in r.ad_group_ad.ad.responsive_search_ad.headlines]
            descriptions = [d.text for d in r.ad_group_ad.ad.responsive_search_ad.descriptions]

        results.append({
            "id": str(r.ad_group_ad.ad.id),
            "name": r.ad_group_ad.ad.name,
            "type": r.ad_group_ad.ad.type_.name,
            "status": r.ad_group_ad.status.name,
            "ad_group": r.ad_group.name,
            "final_urls": list(r.ad_group_ad.ad.final_urls),
            "headlines": headlines,
            "descriptions": descriptions,
            "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks,
            "cost": cost,
            "conversions": r.metrics.conversions,
            "conversion_value": conv_value,
            "cost_per_conversion": r.metrics.cost_per_conversion / 1_000_000,
            "roas": conv_value / cost if cost else 0,
        })
    return results


# ── Keywords ─────────────────────────────────────────────────────────────────


def get_keywords(campaign_id: str, customer_id: str | None = None) -> list[dict]:
    """Return keyword performance for a campaign."""
    cid = customer_id or config.google_ads.customer_id
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.average_cpc,
            metrics.cost_per_conversion
        FROM keyword_view
        WHERE campaign.id = {campaign_id}
          AND segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
        LIMIT 100
    """
    rows = _query(ga_service, cid, query)
    results = []
    for r in rows:
        cost = r.metrics.cost_micros / 1_000_000
        conv_value = r.metrics.conversions_value
        results.append({
            "keyword": r.ad_group_criterion.keyword.text,
            "match_type": r.ad_group_criterion.keyword.match_type.name,
            "ad_group": r.ad_group.name,
            "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks,
            "cost": cost,
            "conversions": r.metrics.conversions,
            "conversion_value": conv_value,
            "avg_cpc": r.metrics.average_cpc / 1_000_000,
            "cost_per_conversion": r.metrics.cost_per_conversion / 1_000_000,
            "roas": conv_value / cost if cost else 0,
        })
    return results


# ── Search Terms ─────────────────────────────────────────────────────────────


def get_search_terms(campaign_id: str, customer_id: str | None = None) -> list[dict]:
    """Return search term report for a campaign."""
    cid = customer_id or config.google_ads.customer_id
    client = _build_client()
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT
            search_term_view.search_term,
            search_term_view.status,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.cost_per_conversion
        FROM search_term_view
        WHERE campaign.id = {campaign_id}
          AND segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
        LIMIT 100
    """
    rows = _query(ga_service, cid, query)
    results = []
    for r in rows:
        cost = r.metrics.cost_micros / 1_000_000
        conv_value = r.metrics.conversions_value
        results.append({
            "search_term": r.search_term_view.search_term,
            "status": r.search_term_view.status.name,
            "ad_group": r.ad_group.name,
            "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks,
            "cost": cost,
            "conversions": r.metrics.conversions,
            "conversion_value": conv_value,
            "cost_per_conversion": r.metrics.cost_per_conversion / 1_000_000,
            "roas": conv_value / cost if cost else 0,
        })
    return results


# ── Full funnel fetch ────────────────────────────────────────────────────────


def get_full_campaign_data(campaign_id: str, customer_id: str | None = None) -> dict:
    """Fetch the entire funnel for one campaign: ad groups, ads, keywords, search terms."""
    cid = customer_id
    return {
        "campaign_id": campaign_id,
        "ad_groups": get_ad_groups(campaign_id, cid),
        "ads": get_ads(campaign_id, cid),
        "keywords": get_keywords(campaign_id, cid),
        "search_terms": get_search_terms(campaign_id, cid),
    }
