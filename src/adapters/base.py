from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any

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

class BaseSocialClient(ABC):
    """
    Interface canônica para clientes de integração com redes sociais.
    """
    
    reliability_score: float = 0.99
    supported_capabilities: list[str] = []
    cost_per_action: float = 0.0
    latency_ms: int = 0
    
    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Realiza um health check completo de credenciais e cotas."""
        pass

    @abstractmethod
    def publish_image(self, image_path: str, title: str, description: str, destination_link: str) -> PublishedContent:
        """Publica uma imagem na plataforma."""
        pass

    @abstractmethod
    def publish_video(self, video_path: str, title: str, description: str, destination_link: str) -> PublishedContent:
        """Publica um vídeo na plataforma com controle de upload."""
        pass

    @abstractmethod
    def get_metrics(self, content_id: str) -> CanonicalMetrics:
        """Obtém as métricas canônicas de um conteúdo específico."""
        pass

    @abstractmethod
    def archive_content(self, content_id: str) -> bool:
        """Arquiva ou deleta um conteúdo da plataforma."""
        pass
