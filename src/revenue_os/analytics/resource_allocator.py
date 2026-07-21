from enum import Enum
from typing import Dict, Any

class AllocationMode(str, Enum):
    ORGANIC_DISCOVERY = "ORGANIC_DISCOVERY"
    PAID_SCALING = "PAID_SCALING"

class ResourceType(str, Enum):
    BUDGET_USD = "BUDGET_USD"
    COMPUTE_HOURS = "COMPUTE_HOURS"
    POST_QUOTA = "POST_QUOTA"
    API_CALLS = "API_CALLS"

class ResourceAllocator:
    """
    O Gestor Mestre de Recursos.
    Na Fase 1 (Organic), gerencia tempo e posts para maximizar 'Organic Reward'.
    Na Fase 2 (Paid), gerencia dólares para maximizar 'Economic Reward'.
    """
    def __init__(self, mode: AllocationMode = AllocationMode.ORGANIC_DISCOVERY):
        self.mode = mode
        
    def allocate(self, resource_pool: float, resource_type: ResourceType, candidates: Dict[str, float]) -> Dict[str, float]:
        """
        Recebe o pool de recursos (Ex: 30 posts), os candidatos e seus Rewards matemáticos.
        Retorna a fatia de recurso destinada a cada candidato.
        """
        if not candidates:
            return {}
            
        # O Bandit funciona de forma similar tanto pra grana quanto pra views orgânicas.
        # Ordenamos pelo Reward (Orgânico ou Econômico dependendo do chamador).
        sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        
        allocations = {}
        pool_remaining = resource_pool
        
        # 70% para a Metade Superior (Exploitation)
        exploitation_pool = resource_pool * 0.70
        top_half = sorted_candidates[:max(1, len(sorted_candidates)//2)]
        
        for variant, _ in top_half:
            if pool_remaining <= 0: break
            # Distribui de forma ingênua na metade campeã (no mundo real pesaria pelo delta de reward)
            share = min(exploitation_pool / len(top_half), pool_remaining)
            allocations[variant] = share
            pool_remaining -= share
            
        # 30% para a Metade Inferior (Exploration / Novos Testes)
        bottom_half = sorted_candidates[len(top_half):]
        if bottom_half and pool_remaining > 0:
            for variant, _ in bottom_half:
                if pool_remaining <= 0: break
                share = min(pool_remaining / len(bottom_half), pool_remaining)
                allocations[variant] = share
                pool_remaining -= share
                
        return allocations
