from typing import Dict, Any
from src.revenue_os.analytics.schemas import RealWorldMetrics

class PlatformMetricsAdapter:
    """
    Camada de Tradução Multi-Plataforma.
    Transforma payloads arbitrários de plataformas (YouTube, TikTok, Pinterest)
    no `Canonical Experiment Schema` do Revenue OS.
    """
    
    @staticmethod
    def adapt_youtube_metrics(yt_payload: Dict[str, Any]) -> RealWorldMetrics:
        """
        Exemplo Payload YT:
        {
            "impressions_ctr": 5.2,
            "audience_retention_3s": 42.1,
            "average_view_percentage": 50.5,
            "views": 15000
        }
        """
        return RealWorldMetrics(
            impressions=yt_payload.get("views", 0),
            ctr_percent=yt_payload.get("impressions_ctr", 0.0),
            retention_3s_percent=yt_payload.get("audience_retention_3s", 0.0),
            completion_rate_percent=yt_payload.get("average_view_percentage", 0.0),
            conversion_count=0  # YouTube puramente não costuma dar vendas diretas
        )

    @staticmethod
    def adapt_pinterest_metrics(pin_payload: Dict[str, Any]) -> RealWorldMetrics:
        """
        Exemplo Payload Pinterest:
        {
            "impressions": 50000,
            "outbound_clicks": 150,
            "saves": 300
        }
        Pinterest não tem "retenção de 3s" real em pins estáticos. 
        Mapeamos cliques e engajamento.
        """
        impressions = pin_payload.get("impressions", 1)
        saves = pin_payload.get("saves", 0)
        clicks = pin_payload.get("outbound_clicks", 0)
        
        # O CTR de Pinterest é baseado em cliques de saída (Outbound)
        ctr = (clicks / impressions) * 100 if impressions > 0 else 0.0
        
        # Como Pinterest é majoritariamente visual, "Saves" são um proxy de "Retention" (Intenção mantida)
        proxy_retention = (saves / impressions) * 100 * 10 # Multiplicador de escala
        
        return RealWorldMetrics(
            impressions=impressions,
            ctr_percent=round(ctr, 2),
            retention_3s_percent=round(proxy_retention, 2),
            completion_rate_percent=0.0,
            conversion_count=0
        )
