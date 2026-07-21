import random
import uuid
import math
from datetime import datetime
from typing import List

from src.revenue_os.analytics.schemas import ExperimentContract

class SyntheticRealitySimulator:
    """
    Simulador de Realidade Sintética (Mundo Real / TikTok Mock).
    Agora incorpora Decaimento de Saturação (Exposure / Audience Pool) e Paradoxo de Simpson.
    """
    
    @staticmethod
    def simulate_world_response(
        hypothesis_statement: str, 
        metric_target: str,
        variant_a_desc: str, 
        variant_b_desc: str, 
        n_samples: int = 50,
        causation_bias: str = "A", # Qual variante o "mundo" prefere secretamente
        exposure_count: int = 0, # Quantas pessoas já viram o padrão (para Saturação)
        audience_pool: int = 1000000, # Tamanho do Nicho
        simpson_paradox: bool = False # Se ativado, inverte o bias em nichos locais
    ) -> List[ExperimentContract]:
        
        experiments = []
        
        # Saturação = Exposição / Tamanho da Audiência
        # Quanto mais próximo de 1, mais fadigada a audiência
        saturation = exposure_count / audience_pool if audience_pool > 0 else 1.0
        
        for i in range(n_samples):
            var_id = "A" if i % 2 == 0 else "B"
            desc = variant_a_desc if var_id == "A" else variant_b_desc
            
            impressions = random.randint(1000, 50000)
            
            # Decidindo o "Nicho Local" do clipe (importante para o Paradoxo de Simpson)
            local_niche = "finance" if i % 3 == 0 else ("gaming" if i % 3 == 1 else "lifestyle")
            
            # Aplicando o viés do mundo real
            # No Paradoxo de Simpson, a Variante B amassa nos nichos, mas perde na agregação global.
            actual_bias = causation_bias
            if simpson_paradox and local_niche in ["finance", "gaming"]:
                actual_bias = "B" if causation_bias == "A" else "A"
            
            # Base metrics
            ctr = random.uniform(1.5, 4.0)
            ret_3s = random.uniform(15.0, 30.0)
            
            if var_id == actual_bias:
                if metric_target == "retention_3s":
                    ret_3s += random.uniform(10.0, 25.0)
                elif metric_target == "ctr":
                    ctr += random.uniform(2.0, 4.0)
            
            # Na agregação global do Simpson, forçamos 'A' a receber visualizações gigantescas no nicho 'lifestyle' onde ela ganha
            if simpson_paradox and var_id == causation_bias and local_niche == "lifestyle":
                impressions *= 10
                if metric_target == "retention_3s":
                    ret_3s += 65.0
                else:
                    ctr += 15.0 # Domínio absurdo localizando o peso agregado
                
            # Aplicando o DECAIMENTO POR SATURAÇÃO (Fatigue)
            # CTR = base_ctr * exp(-saturation * 3) (O fator 3 acelera a percepção de fadiga)
            fatigue_multiplier = math.exp(-saturation * 3)
            ctr = ctr * fatigue_multiplier
            ret_3s = ret_3s * fatigue_multiplier
            
            completion = ret_3s * random.uniform(0.3, 0.6)
            
            exp = ExperimentContract(
                experiment_id=f"SYN-{uuid.uuid4().hex[:8].upper()}",
                hypothesis={
                    "statement": hypothesis_statement,
                    "metric_target": metric_target
                },
                variant={
                    "id": var_id,
                    "description": desc
                },
                economics={
                    "generation_cost_usd": random.uniform(0.05, 0.20),
                    "revenue_usd": random.uniform(0, 5.0) if completion > 30 else 0
                },
                creative_hash=uuid.uuid4().hex,
                platform="Tiktok",
                published_at=datetime.utcnow().isoformat() + "Z",
                status="PUBLISHED"
            )
            
            exp.real_world_metrics.impressions = impressions
            exp.real_world_metrics.ctr_percent = round(max(0.1, ctr), 2)
            exp.real_world_metrics.retention_3s_percent = round(min(100.0, max(1.0, ret_3s)), 2)
            exp.real_world_metrics.completion_rate_percent = round(min(100.0, max(1.0, completion)), 2)
            exp.real_world_metrics.conversion_count = int(impressions * (exp.real_world_metrics.completion_rate_percent/100) * 0.001)
            
            exp.calculate_reward()
            
            # Adicionando metadados dinâmicos para queries avançadas (ex: separar por nicho)
            # Como Pydantic model não tem campo arbitrário ativo, vamos acoplar na descrição temporariamente
            exp.variant.description += f" [Niche: {local_niche}]"
            
            experiments.append(exp)
            
        return experiments
