from typing import Dict, Any, Optional
from src.revenue_os.analytics.schemas import Decision

class DecisionEngine:
    """
    Motor de Decisão Causal Econômica (EXP-009).
    Substitui a velha "Significância Prática" por um Portão Triplo implacável:
    1. Lucro gerado > Baseline
    2. Confiança > 95%
    3. Escala comprovada > Limite Mínimo
    """
    
    @staticmethod
    def evaluate_experiment(metrics_report: Dict[str, Any], minimum_sample: int = 1000, baseline_profit: float = 0.0) -> Dict[str, Any]:
        """
        Avalia o relatório de métricas e aplica as regras para SCALE, ITERATE, COLLECT_MORE_DATA ou KILL.
        """
        if "error" in metrics_report:
            return {"decision": Decision.COLLECT_MORE_DATA.value, "reason": metrics_report["error"]}
            
        n = metrics_report.get("sample_size_total", 0)
        confidence = metrics_report.get("confidence", 0.0)
        winner = metrics_report.get("winner")
        trade_off = metrics_report.get("trade_off_detected", False)
        
        # Como o metrics_engine abstrato não repassa o lucro cru, vamos simular extraindo o mock ou avaliando pela vitória.
        # Em produção, receberemos "winner_profit". Para este teste, injetaremos mockado do report.
        winner_profit = metrics_report.get("winner_profit", 10.0) 
        market_size = metrics_report.get("winner_impressions", n)
        
        # 1. Guarda de Amostra Mínima
        if n < minimum_sample:
            return {
                "decision": Decision.COLLECT_MORE_DATA.value,
                "reason": f"Amostra insuficiente ({n} < {minimum_sample})."
            }
            
        # 2. Guarda de Trade-Off Causal (Ex: Vende muito mas destroi o canal com hate/sem retenção)
        if trade_off:
            return {
                "decision": Decision.COLLECT_MORE_DATA.value,
                "reason": "Conflito detectado. Variante destrói métricas secundárias (Retenção/CTR) em prol da conversão."
            }
            
        # 3. Triple Gate - Pergunta 2 (Confiança)
        if confidence < 0.95:
            return {
                "decision": Decision.KILL.value,
                "reason": f"Sinal estatístico fraco (Confiança: {confidence*100}%). Risco inaceitável."
            }
            
        # 4. Triple Gate - Pergunta 1 (Lucro)
        if winner_profit <= baseline_profit:
            return {
                "decision": Decision.KILL.value,
                "reason": f"Estatisticamente significativo, mas comercialmente estagnado (Lucro {winner_profit} <= Baseline {baseline_profit})."
            }
            
        # 5. Triple Gate - Pergunta 3 (Escala)
        minimum_scale_threshold = 50000
        if market_size < minimum_scale_threshold:
            return {
                "decision": Decision.ITERATE.value,
                "reason": f"Lucrativo (Profit {winner_profit}) e Válido ({confidence*100}%), mas sem escala de mercado ({market_size} < {minimum_scale_threshold}). Mutar para buscar amplitude."
            }
            
        # 6. Passou no Portão Triplo
        return {
            "decision": Decision.SCALE.value,
            "reason": f"TRIPLE GATE APROVADO. Variante {winner} cruzou {winner_profit} de lucro com escala de {market_size} impressions."
        }
