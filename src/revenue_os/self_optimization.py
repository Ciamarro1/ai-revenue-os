from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class SelfOptimizationEngine:
    """
    Self-Optimization Engine do AI Revenue OS (Sprint 14).
    Analisa a própria saúde operacional da plataforma:
    - Identifica gargalos de execução
    - Detecta skills subutilizadas ou ineficientes
    - Ajusta dinamicamente a relação de Exploração vs Explotação
    - Recomenda refatorações ou tuning de parâmetros
    """

    def __init__(self, current_exploration_ratio: float = 0.30):
        self.exploration_ratio = current_exploration_ratio
        self.exploitation_ratio = 1.0 - current_exploration_ratio

    def run_health_and_optimization_audit(self, skill_telemetry: Optional[List[Dict[str, Any]]] = None, average_roi: float = 3.2) -> Dict[str, Any]:
        """
        Executa auditoria de auto-otimização do runtime.
        """
        bottlenecks = []
        recommendations = []

        # 1. Ajuste Automático da Razão Exploração / Explotação
        if average_roi >= 3.0 and self.exploration_ratio > 0.15:
            self.exploration_ratio = max(0.15, round(self.exploration_ratio - 0.05, 2))
            self.exploitation_ratio = round(1.0 - self.exploration_ratio, 2)
            recommendations.append(f"ROI elevado ({average_roi:.1f}x): Reduzida taxa de exploração para {self.exploration_ratio*100:.0f}% e aumentada explotação para {self.exploitation_ratio*100:.0f}%.")
        elif average_roi < 1.5 and self.exploration_ratio < 0.50:
            self.exploration_ratio = min(0.50, round(self.exploration_ratio + 0.10, 2))
            self.exploitation_ratio = round(1.0 - self.exploration_ratio, 2)
            recommendations.append(f"ROI baixo ({average_roi:.1f}x): Aumentada taxa de exploração para {self.exploration_ratio*100:.0f}% para descobrir novos genomas vitoriosos.")

        # 2. Diagnóstico de Gargalos em Telemetria
        if skill_telemetry:
            for skill in skill_telemetry:
                name = skill.get("name", "skill")
                avg_latency = skill.get("avg_latency_sec", 0.0)
                success_rate = skill.get("success_rate", 1.0)

                if avg_latency > 10.0:
                    bottlenecks.append(f"Skill '{name}' apresenta latência elevada ({avg_latency:.1f}s). Recomenda-se cache ou execução assíncrona.")
                if success_rate < 0.85:
                    recommendations.append(f"Skill '{name}' possui taxa de sucesso baixa ({success_rate*100:.0f}%). Sugere-se revisão nos seletores e validação de schema.")

        return {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "health_status": "HEALTHY" if len(bottlenecks) == 0 else "WARNING",
            "current_ratios": {
                "exploration": self.exploration_ratio,
                "exploitation": self.exploitation_ratio
            },
            "detected_bottlenecks": bottlenecks,
            "optimization_recommendations": recommendations
        }

    def suggest_architectural_optimizations(self, skill_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Recomenda trocas de ferramentas arquiteturais quando a latência ou taxa de erro atinge limiares críticos.
        """
        suggestions = []
        for m in skill_metrics:
            skill_name = m.get("name", "UnknownSkill")
            latency = m.get("latency_sec", 0.0)
            failure_rate = m.get("failure_rate", 0.0)

            if latency > 4.0:
                suggestions.append({
                    "skill": skill_name,
                    "issue": f"Latência de {latency:.1f}s excede limiar ideal de 4.0s",
                    "architectural_suggestion": "Substituir biblioteca por alternativa compilada (C++/Rust/Go) do OSS Catalog",
                    "expected_cost_reduction_percent": 38.0
                })

            if failure_rate > 0.15:
                suggestions.append({
                    "skill": skill_name,
                    "issue": f"Taxa de falha de {failure_rate*100:.1f}% acima do tolerado (15%)",
                    "architectural_suggestion": "Trocar estratégia de seletores para Playwright com fallback de Visão LLM",
                    "expected_reliability_increase_percent": 25.0
                })
        return suggestions
