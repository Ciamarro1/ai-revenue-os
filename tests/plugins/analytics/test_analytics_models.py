from src.revenue_os.plugins.analytics.models import (
    MetricProvenance,
    AnalyticsEventPayload,
    AffiliateCallbackPayload,
    AnalyticsPluginHealth,
    AnalyticsConfig
)

def test_metric_provenance_schema():
    p = MetricProvenance(provenance_type="REAL_PRODUCTION", signature_verified=True)
    assert p.provenance_type == "REAL_PRODUCTION"
    assert p.signature_verified is True
    assert len(p.trace_id) > 0

def test_analytics_event_payload_schema():
    ev = AnalyticsEventPayload(event_name="checkout_click", properties={"price": 99.0})
    assert ev.event_name == "checkout_click"
    assert ev.properties["price"] == 99.0

def test_affiliate_callback_payload_schema():
    cb = AffiliateCallbackPayload(platform="hotmart", transaction_id="TX123", amount=100.0, commission=50.0)
    assert cb.platform == "hotmart"
    assert cb.commission == 50.0

def test_analytics_config_schema():
    cfg = AnalyticsConfig(webhook_secret="test_secret")
    assert cfg.webhook_secret == "test_secret"
