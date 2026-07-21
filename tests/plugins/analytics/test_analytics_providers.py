from src.revenue_os.plugins.analytics.providers import (
    GA4AnalyticsProvider,
    PostHogAnalyticsProvider,
    ResendAnalyticsProvider,
    AffiliateCallbackProcessor,
    SignedWebhookManager
)
from src.revenue_os.plugins.analytics.models import AnalyticsEventPayload

def test_ga4_provider_unconfigured():
    ga4 = GA4AnalyticsProvider()
    assert ga4.is_enabled is False
    
    ev = AnalyticsEventPayload(event_name="test")
    res = ga4.track_event(ev)
    assert res["status"] == "WAITING_EXTERNAL_DEPENDENCY"
    assert res["provenance"]["provenance_type"] == "WAITING_EXTERNAL_DEPENDENCY"

def test_posthog_provider_unconfigured():
    ph = PostHogAnalyticsProvider()
    assert ph.is_enabled is False
    
    ev = AnalyticsEventPayload(event_name="test")
    res = ph.track_event(ev)
    assert res["status"] == "WAITING_EXTERNAL_DEPENDENCY"

def test_resend_provider_unconfigured():
    r = ResendAnalyticsProvider()
    assert r.is_enabled is False
    
    ev = AnalyticsEventPayload(event_name="test")
    res = r.track_event(ev)
    assert res["status"] == "WAITING_EXTERNAL_DEPENDENCY"

def test_affiliate_callback_processor():
    proc = AffiliateCallbackProcessor()
    
    # Hotmart
    res_h = proc.process_callback("hotmart", {"transaction": "HP100", "purchase": {"price": {"value": 200.0}}})
    assert res_h.platform == "hotmart"
    assert res_h.transaction_id == "HP100"
    assert res_h.amount == 200.0
    
    # Kiwify
    res_k = proc.process_callback("kiwify", {"order_id": "KW200", "order_ref_amount": 15000})
    assert res_k.platform == "kiwify"
    assert res_k.amount == 150.0

def test_signed_webhook_manager():
    mgr = SignedWebhookManager("secret_key")
    payload = {"event": "sale", "amount": 100}
    
    sig = mgr.sign_payload(payload)
    assert len(sig) > 0
    assert mgr.verify_signature(payload, sig) is True
    assert mgr.verify_signature(payload, "invalid_signature") is False
