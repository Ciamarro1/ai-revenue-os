from typing import Dict, Any, List

class ReliabilityMetricsEngine:
    """
    Motor de Métricas de Confiabilidade de Receita (RRI) e Qualidade do Conhecimento (KQI) (v5.5 LTS).
    """

    def calculate_rri(
        self,
        recent_rois: List[float],
        conversion_rate: float = 0.03,
        model_confidence: float = 0.88,
        reproducibility_rate: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calcula o Revenue Reliability Index (RRI: 0-100).
        """
        if not recent_rois:
            return {"rri_score": 0.0, "level": "NO_DATA"}

        mean_roi = sum(recent_rois) / len(recent_rois)
        variance = sum((r - mean_roi) ** 2 for r in recent_rois) / max(1, len(recent_rois))
        stability_score = max(0.0, min(30.0, 30.0 - (variance * 2.0)))

        roi_score = max(0.0, min(30.0, mean_roi * 10.0))
        conf_score = model_confidence * 20.0
        reprod_score = reproducibility_rate * 20.0

        rri_total = round(stability_score + roi_score + conf_score + reprod_score, 1)

        return {
            "rri_score": rri_total,
            "mean_roi": round(mean_roi, 2),
            "roi_variance": round(variance, 2),
            "reliability_level": "HIGHLY_RELIABLE" if rri_total >= 80 else ("MODERATE" if rri_total >= 50 else "UNSTABLE")
        }

    def calculate_kqi(
        self,
        confirmed_rules_count: int,
        rejected_rules_count: int,
        reuse_rate: float = 0.85,
        decision_contribution_rate: float = 0.90
    ) -> Dict[str, Any]:
        """
        Calcula o Knowledge Quality Index (KQI: 0-100).
        """
        total = confirmed_rules_count + rejected_rules_count
        if total == 0:
            return {"kqi_score": 0.0, "quality_level": "NO_KNOWLEDGE"}

        confirmation_ratio = confirmed_rules_count / total
        ratio_score = confirmation_ratio * 40.0
        reuse_score = reuse_rate * 30.0
        decision_score = decision_contribution_rate * 30.0

        kqi_total = round(ratio_score + reuse_score + decision_score, 1)

        return {
            "kqi_score": kqi_total,
            "confirmation_ratio": round(confirmation_ratio, 2),
            "quality_level": "HIGH_QUALITY" if kqi_total >= 80 else ("ACCEPTABLE" if kqi_total >= 50 else "LOW_QUALITY")
        }
