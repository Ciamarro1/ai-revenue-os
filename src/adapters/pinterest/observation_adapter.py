from typing import List
from src.ports.observation_adapter import ObservationAdapter
from src.core.cognition.models import Observation
from src.integrations.pinterest.analytics import AnalyticsManager

class PinterestObservationAdapter(ObservationAdapter):
    """
    Pinterest Observation Adapter (Sprint 6.3).
    Converte as CanonicalMetrics recuperadas do Pinterest em Observations estruturadas.
    """
    def __init__(self, analytics_manager: AnalyticsManager):
        self.analytics_manager = analytics_manager

    def fetch_observations(self, content_id: str) -> List[Observation]:
        metrics = self.analytics_manager.get_metrics(content_id)
        obs_list = []
        
        if metrics.impressions is not None:
            obs_list.append(Observation(
                source="pinterest_api",
                metric_name="Impressions",
                value=float(metrics.impressions),
                raw_data=f"content_id: {content_id}"
            ))
        if metrics.outbound_clicks is not None:
            obs_list.append(Observation(
                source="pinterest_api",
                metric_name="OutboundClicks",
                value=float(metrics.outbound_clicks),
                raw_data=f"content_id: {content_id}"
            ))
        if metrics.saves is not None:
            obs_list.append(Observation(
                source="pinterest_api",
                metric_name="Saves",
                value=float(metrics.saves),
                raw_data=f"content_id: {content_id}"
            ))
            
        return obs_list
