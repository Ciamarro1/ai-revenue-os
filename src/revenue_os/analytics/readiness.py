from typing import Dict, Any

class AutonomousReadinessGate:
    """
    O último portão antes do modo LIVE.
    Bifurcado em duas esteiras:
    - Synthetic Readiness: Libera o laboratório e o Canary (ambiente de teste/seguro).
    - Production Readiness: Libera a automação plena e gastos de GPU/API em larga escala.
    """
    def __init__(self):
        pass
        
    def evaluate(self, genome_learning_score: float, safety_score: float, factory_reliability: float, audit_completeness: float) -> Dict[str, Any]:
        is_synthetic_ready = True
        is_production_ready = True
        synthetic_reasons = []
        production_reasons = []
        
        # Synthetic Evaluation (Laboratório)
        if genome_learning_score <= 0.75:
            is_synthetic_ready = False
            synthetic_reasons.append(f"Genome Learning insuficiente ({genome_learning_score:.2f} <= 0.75). O sistema não convergiu padrões no ambiente simulado.")
            
        if safety_score <= 0.90:
            is_synthetic_ready = False
            synthetic_reasons.append(f"Safety Score insuficiente ({safety_score:.2f} <= 0.90). Risco de banimento detectado.")
            
        # Production Evaluation (Mundo Real / Custos)
        if not is_synthetic_ready:
            is_production_ready = False
            production_reasons.append("Não possui maturidade sintética (Falhou no Synthetic Readiness).")
            
        if factory_reliability <= 0.90:
            is_production_ready = False
            production_reasons.append(f"Factory Reliability insuficiente ({factory_reliability:.2f} <= 0.90). A infraestrutura física de renderização (MPT) está instável.")
            
        if audit_completeness < 1.0:
            is_production_ready = False
            production_reasons.append("Auditoria física e de dependências incompleta.")
            
        return {
            "synthetic_authorized": is_synthetic_ready,
            "production_authorized": is_production_ready,
            "readiness_score": (genome_learning_score + safety_score + factory_reliability) / 3.0,
            "synthetic_blockers": synthetic_reasons,
            "production_blockers": production_reasons
        }
