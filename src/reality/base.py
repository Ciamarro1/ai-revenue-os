from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from src.reality.research.schemas import ResearchReport

@dataclass
class PublishedContent:
    content_id: str
    platform: str
    status: str
    published_at: Optional[str] = None
    url: Optional[str] = None
    confidence: float = 1.0
    provider: str = "api"

@dataclass
class CanonicalMetrics:
    impressions: int
    outbound_clicks: int
    saves: int
    spend: Optional[float] = None
    revenue: Optional[float] = None
    confidence: float = 1.0
    provider: str = "api"

class CapabilityProvider(ABC):
    """Interface base para qualquer provedor da Camada de Realidade."""
    confidence_score: float = 1.0
    provider_name: str = "unknown"
    
    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Retorna o status de saúde do provedor."""
        pass

class Publisher(CapabilityProvider):
    """Contrato para provedores capazes de publicar mídia."""
    
    @abstractmethod
    def publish_image(self, image_path: str, title: str, description: str, destination_link: str) -> PublishedContent:
        pass

    @abstractmethod
    def publish_video(self, video_path: str, title: str, description: str, destination_link: str) -> PublishedContent:
        pass

    @abstractmethod
    def archive_content(self, content_id: str) -> bool:
        pass

class MetricsProvider(CapabilityProvider):
    """Contrato para provedores capazes de coletar métricas reais."""
    
    @abstractmethod
    def get_metrics(self, content_id: str) -> CanonicalMetrics:
        pass

class TrendProvider(CapabilityProvider):
    """Contrato para provedores capazes de descobrir tendências."""
    
    @abstractmethod
    def discover_trend(self) -> Dict[str, Any]:
        pass

class ResearchProvider(CapabilityProvider):
    """Contrato para provedores capazes de conduzir pesquisas na web e retornar relatórios estruturados."""
    
    @abstractmethod
    def execute_research(self, query: str, context: Optional[Dict[str, Any]] = None) -> ResearchReport:
        pass

class CapabilityRegistry:
    """
    Registro Universal de Capacidades.
    Permite que o Experiment Runner peça por uma capacidade ("quem pode publicar?")
    em vez de acoplar a um provedor específico.
    """
    def __init__(self):
        self.publishers: List[Publisher] = []
        self.metrics_providers: List[MetricsProvider] = []
        self.trend_providers: List[TrendProvider] = []
        self.research_providers: List[ResearchProvider] = []
        
    def register_publisher(self, provider: Publisher):
        self.publishers.append(provider)
        # Ordena por confiança decrescente (os mais confiáveis primeiro)
        self.publishers.sort(key=lambda p: p.confidence_score, reverse=True)
        
    def register_metrics_provider(self, provider: MetricsProvider):
        self.metrics_providers.append(provider)
        self.metrics_providers.sort(key=lambda p: p.confidence_score, reverse=True)
        
    def register_trend_provider(self, provider: TrendProvider):
        self.trend_providers.append(provider)
        self.trend_providers.sort(key=lambda p: p.confidence_score, reverse=True)
        
    def register_research_provider(self, provider: ResearchProvider):
        self.research_providers.append(provider)
        self.research_providers.sort(key=lambda p: p.confidence_score, reverse=True)

    def get_best_publisher(self) -> Optional[Publisher]:
        return self.publishers[0] if self.publishers else None
        
    def get_best_metrics_provider(self) -> Optional[MetricsProvider]:
        return self.metrics_providers[0] if self.metrics_providers else None
        
    def get_best_trend_provider(self) -> Optional[TrendProvider]:
        return self.trend_providers[0] if self.trend_providers else None
        
    def get_best_researcher(self) -> Optional[ResearchProvider]:
        return self.research_providers[0] if self.research_providers else None
