from typing import Optional
import random
from src.revenue_os.analytics.schemas import ExperimentContract, RealWorldMetrics

class RealityMetricsProvider:
    """
    Abstrai a busca de métricas físicas na API da plataforma (ex: Pinterest).
    """
    def fetch(self, exp: ExperimentContract) -> RealWorldMetrics:
        # Aqui conectaria com Pinterest API SDK usando o exp.experiment_id
        # Para este escopo da arquitetura mockaremos uma resposta de API
        impressions = random.randint(100, 10000)
        clicks = int(impressions * random.uniform(0.01, 0.10))
        saves = int(clicks * random.uniform(0.0, 0.30))
        
        return RealWorldMetrics(
            impressions=impressions,
            ctr_percent=(clicks / max(1, impressions)) * 100.0,
            retention_3s_percent=random.uniform(40.0, 70.0),
            landing_visit_percent=random.uniform(60.0, 90.0),
            conversion_count=saves,
            profit_usd=saves * 1.50 # Estimativa genérica
        )
