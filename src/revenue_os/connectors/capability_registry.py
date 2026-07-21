from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class CapabilityConfig(BaseModel):
    capability_name: str
    primary_provider: str
    fallbacks: List[str] = Field(default_factory=list)
    description: str = ""

class CapabilityRegistry:
    """
    Registry Central de Capacidades (Sprint 9.7).
    Gerencia a associação entre capacidades solicitadas pelo Economic Brain
    e os provedores Open Source homologados (Primário + Fallbacks).
    """

    def __init__(self):
        self._capabilities: Dict[str, CapabilityConfig] = {}
        self._load_default_capabilities()

    def _load_default_capabilities(self) -> None:
        defaults = [
            CapabilityConfig(capability_name="landing_generation", primary_provider="astro", fallbacks=["nextjs", "hugo"], description="Geração de Landing Pages estáticas e SSG"),
            CapabilityConfig(capability_name="video_generation", primary_provider="money_printer_turbo", fallbacks=["moviepy", "ffmpeg"], description="Geração de vídeos verticais curtos 9:16"),
            CapabilityConfig(capability_name="browser_automation", primary_provider="playwright", fallbacks=["puppeteer", "selenium"], description="Automação headless de redes sociais e scraping"),
            CapabilityConfig(capability_name="vector_database", primary_provider="qdrant", fallbacks=["chroma", "milvus"], description="Banco de dados vetorial para RAG e busca semântica"),
            CapabilityConfig(capability_name="analytics_dashboard", primary_provider="grafana", fallbacks=["metabase", "apache_superset"], description="Visualização de dashboards e telemetria"),
            CapabilityConfig(capability_name="marketplace_connectors", primary_provider="hotmart", fallbacks=["clickbank", "amazon", "digistore24", "gumroad"], description="Adaptadores de afiliados de marketplaces")
        ]
        for cap in defaults:
            self.register_capability(cap)

    def register_capability(self, config: CapabilityConfig) -> None:
        self._capabilities[config.capability_name.lower()] = config

    def get_provider(self, capability_name: str) -> str:
        cap = self._capabilities.get(capability_name.lower())
        if cap:
            return cap.primary_provider
        return "default_provider"

    def get_fallbacks(self, capability_name: str) -> List[str]:
        cap = self._capabilities.get(capability_name.lower())
        if cap:
            return cap.fallbacks
        return []

    def get_capability(self, capability_name: str) -> Optional[CapabilityConfig]:
        return self._capabilities.get(capability_name.lower())
