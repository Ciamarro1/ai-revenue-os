from src.revenue_os.plugins.affiliates.providers import (
    HotmartProvider,
    KiwifyProvider,
    EduzzProvider,
    AmazonProvider
)
from src.revenue_os.plugins.affiliates.models import DeepLinkRequest

def test_hotmart_provider_operations():
    provider = HotmartProvider()
    assert provider.provider_name == "hotmart"
    
    products = provider.discover_products("tech", limit=2)
    assert len(products) == 2
    assert products[0].marketplace == "Hotmart"
    
    details = provider.get_offer_details(products[0].id)
    assert details.marketplace == "Hotmart"
    
    rules = provider.get_commission_rules(products[0].id)
    assert rules.marketplace == "Hotmart"
    
    link = provider.generate_deep_link(DeepLinkRequest(product_id=products[0].id, sub_id="c1"))
    assert "go.hotmart.com" in link.tracking_url
    assert link.sub_id == "c1"

def test_kiwify_provider_operations():
    provider = KiwifyProvider()
    assert provider.provider_name == "kiwify"
    
    products = provider.discover_products("marketing", limit=2)
    assert len(products) == 2
    assert products[0].marketplace == "Kiwify"
    
    details = provider.get_offer_details(products[0].id)
    assert details.marketplace == "Kiwify"
    
    rules = provider.get_commission_rules(products[0].id)
    assert rules.marketplace == "Kiwify"
    
    link = provider.generate_deep_link(DeepLinkRequest(product_id=products[0].id, sub_id="c2"))
    assert "pay.kiwify.com.br" in link.tracking_url

def test_eduzz_provider_operations():
    provider = EduzzProvider()
    assert provider.provider_name == "eduzz"
    
    products = provider.discover_products("finance", limit=2)
    assert len(products) == 2
    assert products[0].marketplace == "Eduzz"
    
    details = provider.get_offer_details(products[0].id)
    assert details.marketplace == "Eduzz"
    
    rules = provider.get_commission_rules(products[0].id)
    assert rules.marketplace == "Eduzz"
    
    link = provider.generate_deep_link(DeepLinkRequest(product_id=products[0].id, sub_id="c3"))
    assert "sun.eduzz.com" in link.tracking_url

def test_amazon_provider_operations():
    provider = AmazonProvider()
    assert provider.provider_name == "amazon"
    
    products = provider.discover_products("gear", limit=2)
    assert len(products) == 2
    assert products[0].marketplace == "Amazon"
    
    details = provider.get_offer_details(products[0].id)
    assert details.marketplace == "Amazon"
    
    rules = provider.get_commission_rules(products[0].id)
    assert rules.marketplace == "Amazon"
    
    link = provider.generate_deep_link(DeepLinkRequest(product_id=products[0].id, sub_id="c4"))
    assert "amazon.com/dp" in link.tracking_url
