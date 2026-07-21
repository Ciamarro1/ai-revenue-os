import random
import uuid
import math
from typing import List, Dict, Any

from src.revenue_os.analytics.schemas import ExperimentContract

class RevenueSimulator:
    """
    Laboratório Sintético Econômico (EXP-009).
    Simula o choque entre 'Atenção' e 'Venda', provando que ROAS depende do Funil inteiro.
    """
    
    @staticmethod
    def simulate_economic_funnel(
        niche: str,
        base_traffic: int,
        variant_profiles: Dict[str, str], # Ex: {"A": "attention_first", "B": "commercial", "C": "hybrid"}
        n_samples_per_variant: int = 10
    ) -> List[ExperimentContract]:
        
        experiments = []
        
        for variant_id, profile in variant_profiles.items():
            for _ in range(n_samples_per_variant):
                # Variáveis base de mercado
                aov = 49.0
                margin = 0.35
                media_cost = 0.05 * (base_traffic / 1000) # CPM simulação
                
                # Dinâmica de Trade-Off: Atenção vs Intenção
                if profile == "attention_first":
                    # Alto alcance orgânico, baixíssima intenção de compra
                    impressions = base_traffic * random.uniform(1.2, 2.0)
                    retention = random.uniform(40.0, 60.0)
                    ctr = random.uniform(1.0, 2.5) # CTAs moles, as pessoas não saem da plataforma
                    landing_visit = random.uniform(30.0, 50.0) # Muita fuga antes da página carregar
                    conversion = random.uniform(0.5, 1.5) # Conversão péssima, lead desqualificado
                    
                elif profile == "commercial":
                    # Baixo alcance (plataforma corta o alcance por ser "propaganda"), alta intenção
                    impressions = base_traffic * random.uniform(0.1, 0.4) # Algoritmo estrangula o Hard Sell
                    retention = random.uniform(10.0, 25.0)
                    ctr = random.uniform(4.0, 8.0) # Quem fica, clica.
                    landing_visit = random.uniform(60.0, 80.0)
                    conversion = random.uniform(3.0, 6.0) # Conversão brutal
                    
                else: # hybrid
                    # Equilíbrio de ouro
                    impressions = base_traffic * random.uniform(0.8, 1.2)
                    retention = random.uniform(30.0, 45.0)
                    ctr = random.uniform(2.5, 5.0)
                    landing_visit = random.uniform(50.0, 70.0)
                    conversion = random.uniform(2.0, 3.5)
                
                # Adicionando ruído
                completion = retention * random.uniform(0.4, 0.7)
                
                # Execução do Funil Físico
                visitors = int(impressions * (ctr/100) * (landing_visit/100))
                buyers = int(visitors * (conversion/100))
                
                revenue = buyers * aov
                profit = (revenue * margin) - media_cost
                
                exp = ExperimentContract(
                    experiment_id=f"REV-{uuid.uuid4().hex[:6].upper()}",
                    hypothesis={
                        "statement": f"Testing {profile} trade-offs",
                        "metric_target": "profit_usd"
                    },
                    variant={
                        "id": variant_id,
                        "description": profile
                    },
                    economics={
                        "generation_cost_usd": media_cost,
                        "revenue_usd": revenue
                    },
                    creative_hash=uuid.uuid4().hex
                )
                
                exp.real_world_metrics.impressions = int(impressions)
                exp.real_world_metrics.ctr_percent = round(ctr, 2)
                exp.real_world_metrics.retention_3s_percent = round(retention, 2)
                exp.real_world_metrics.completion_rate_percent = round(completion, 2)
                exp.real_world_metrics.landing_visit_percent = round(landing_visit, 2)
                exp.real_world_metrics.conversion_count = buyers
                exp.real_world_metrics.aov_usd = aov
                exp.real_world_metrics.profit_usd = round(profit, 2)
                
                exp.calculate_reward()
                
                experiments.append(exp)
                
        return experiments
