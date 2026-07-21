from src.revenue_os.plugins.affiliates.models import (
    AffiliateProduct,
    OfferDetails,
    CommissionRule,
    DeepLinkRequest,
    DeepLinkResponse,
    AffiliateProviderHealth
)

def test_affiliate_product_schema():
    p = AffiliateProduct(
        id="PROD-1",
        marketplace="Hotmart",
        name="Curso Python",
        price_usd=99.0,
        commission_rate=0.60
    )
    assert p.id == "PROD-1"
    assert p.marketplace == "Hotmart"
    assert p.commission_rate == 0.60
    assert p.classification_status == "LOCAL_TEST"

def test_offer_details_schema():
    d = OfferDetails(
        product_id="PROD-1",
        marketplace="Kiwify",
        description="Descrição do produto",
        guarantee_days=14
    )
    assert d.product_id == "PROD-1"
    assert d.guarantee_days == 14

def test_commission_rule_schema():
    r = CommissionRule(
        product_id="PROD-1",
        marketplace="Eduzz",
        attribution_type="LAST_CLICK",
        commission_percentage=50.0
    )
    assert r.attribution_type == "LAST_CLICK"

def test_deep_link_schemas():
    req = DeepLinkRequest(product_id="PROD-1", sub_id="camp_01")
    resp = DeepLinkResponse(product_id="PROD-1", marketplace="Amazon", tracking_url="https://amazon.com/dp/PROD-1?tag=aff-20&ascsubtag=camp_01")
    
    assert req.sub_id == "camp_01"
    assert "camp_01" in resp.tracking_url
