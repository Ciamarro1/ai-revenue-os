from typing import List, Dict, Any

class AttributionEngine:
    """
    Motor de Atribuição Econômica.
    Decide qual variante ou experimento leva o crédito pelo "Revenue".
    Modelo Atual Híbrido: 40% First Touch, 40% Last Touch, 20% Time Decay (Middle).
    """

    def __init__(self, first_touch_weight: float = 0.40, last_touch_weight: float = 0.40, decay_weight: float = 0.20):
        self.first_touch_weight = first_touch_weight
        self.last_touch_weight = last_touch_weight
        self.decay_weight = decay_weight

    def distribute_revenue(self, touchpoints: List[Dict[str, Any]], total_revenue: float) -> Dict[str, float]:
        """
        Recebe uma lista cronológica de interações (touchpoints) e um montante financeiro.
        Retorna um mapa de {experiment_id: revenue_credit}.
        Ex touchpoint: {"experiment_id": "EXP-009-001", "timestamp": "2026-07-11T10:00:00Z"}
        """
        if not touchpoints:
            return {}

        n_touches = len(touchpoints)
        credit_map = {}
        
        # Inicializa o mapa com 0
        for touch in touchpoints:
            exp_id = touch["experiment_id"]
            if exp_id not in credit_map:
                credit_map[exp_id] = 0.0

        if n_touches == 1:
            credit_map[touchpoints[0]["experiment_id"]] += total_revenue
            return credit_map
            
        if n_touches == 2:
            credit_map[touchpoints[0]["experiment_id"]] += total_revenue * 0.50
            credit_map[touchpoints[-1]["experiment_id"]] += total_revenue * 0.50
            return credit_map

        # Para >= 3 touches: aplica o 40/40/20
        first_exp = touchpoints[0]["experiment_id"]
        last_exp = touchpoints[-1]["experiment_id"]
        
        credit_map[first_exp] += total_revenue * self.first_touch_weight
        credit_map[last_exp] += total_revenue * self.last_touch_weight
        
        middle_touches = touchpoints[1:-1]
        decay_revenue_pool = total_revenue * self.decay_weight
        
        # Time Decay: Os toques mais recentes (próximos ao last_touch) ganham mais crédito do pool de middle.
        # Vamos usar um peso linear baseado na posição para simplificar o Time Decay inicial
        total_decay_weight = sum([i+1 for i in range(len(middle_touches))])
        
        for idx, touch in enumerate(middle_touches):
            weight = (idx + 1) / total_decay_weight
            credit_map[touch["experiment_id"]] += decay_revenue_pool * weight
            
        # Arredondando para evitar float errors bizarros de contabilidade
        for exp_id in credit_map:
            credit_map[exp_id] = round(credit_map[exp_id], 2)
            
        return credit_map
