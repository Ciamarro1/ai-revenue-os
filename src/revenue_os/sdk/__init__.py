"""
AI Revenue OS Plugin SDK (v5.5 LTS)
Permite o desenvolvimento de plugins desacoplados sem expor ou alterar o Kernel proprietário.
"""

from src.revenue_os.plugins.base_plugin import BasePlugin
from src.revenue_os.events.domain_events import DomainEvent
from src.revenue_os.domain.business_asset import BusinessAsset
from src.revenue_os.domain.offer_manifest import OfferManifest
from src.revenue_os.plugins.certification import PluginCertificationEngine

__all__ = [
    "BasePlugin",
    "DomainEvent",
    "BusinessAsset",
    "OfferManifest",
    "PluginCertificationEngine"
]
