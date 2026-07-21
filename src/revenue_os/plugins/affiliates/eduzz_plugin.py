from typing import Dict, Any, Optional
from src.revenue_os.plugins.base_plugin import BasePlugin
from src.revenue_os.plugins.affiliates.providers.eduzz_provider import EduzzProvider
from src.revenue_os.plugins.affiliates.models import DeepLinkRequest

class EduzzAffiliatePlugin(BasePlugin):
    """
    EduzzAffiliatePlugin (Sprint O2).
    Plugin estendendo BasePlugin SDK para integração total com Eduzz.
    """

    def __init__(self, provider: Optional[EduzzProvider] = None):
        self.provider = provider or EduzzProvider()
        self._initialized = False

    @property
    def plugin_name(self) -> str:
        return "eduzz_affiliate_plugin"

    @property
    def category(self) -> str:
        return "marketplaces"

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return self.provider.health_check().model_dump()

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "discover_products")
        niche = payload.get("niche", "general")
        limit = payload.get("limit", 10)
        product_id = payload.get("product_id", "")

        if action == "discover_products":
            products = self.provider.discover_products(niche, limit)
            return {"status": "SUCCESS", "action": action, "products": [p.model_dump() for p in products]}

        elif action == "get_offer_details":
            details = self.provider.get_offer_details(product_id)
            return {"status": "SUCCESS", "action": action, "offer_details": details.model_dump()}

        elif action == "get_commission_rules":
            rules = self.provider.get_commission_rules(product_id)
            return {"status": "SUCCESS", "action": action, "commission_rules": rules.model_dump()}

        elif action == "generate_deep_link":
            req = DeepLinkRequest(
                product_id=product_id,
                affiliate_id=payload.get("affiliate_id", "default_aff"),
                sub_id=payload.get("sub_id")
            )
            link = self.provider.generate_deep_link(req)
            return {"status": "SUCCESS", "action": action, "deep_link": link.model_dump()}

        raise ValueError(f"Ação desconhecida '{action}' para EduzzAffiliatePlugin")

    def shutdown(self) -> None:
        self._initialized = False
