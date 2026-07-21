from src.revenue_os.plugins.affiliates.hotmart_plugin import HotmartAffiliatePlugin
from src.revenue_os.plugins.affiliates.kiwify_plugin import KiwifyAffiliatePlugin
from src.revenue_os.plugins.affiliates.eduzz_plugin import EduzzAffiliatePlugin
from src.revenue_os.plugins.affiliates.amazon_plugin import AmazonAffiliatePlugin
from src.revenue_os.plugins.affiliates.factory import AffiliatePluginFactory
from src.revenue_os.plugins.affiliates.config import AffiliatePluginConfig
from src.revenue_os.plugins.affiliates.models import (
    AffiliateProduct,
    OfferDetails,
    CommissionRule,
    DeepLinkRequest,
    DeepLinkResponse,
    AffiliateProviderHealth
)

__all__ = [
    "HotmartAffiliatePlugin",
    "KiwifyAffiliatePlugin",
    "EduzzAffiliatePlugin",
    "AmazonAffiliatePlugin",
    "AffiliatePluginFactory",
    "AffiliatePluginConfig",
    "AffiliateProduct",
    "OfferDetails",
    "CommissionRule",
    "DeepLinkRequest",
    "DeepLinkResponse",
    "AffiliateProviderHealth",
]
