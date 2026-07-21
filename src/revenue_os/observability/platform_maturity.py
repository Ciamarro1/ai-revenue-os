from typing import Dict, Any

class PlatformMaturityEngine:
    """
    Platform Maturity Index (PMI) Engine (v5.0).
    Avalia quantitativamente a maturidade operacional e o progresso do AI Revenue OS
    em uma escala de 0 a 100 pontos dividida em 9 dimensões de produção.
    """

    def calculate_pmi(
        self,
        auto_publishing_ready: bool = True,
        analytics_tracking_ready: bool = True,
        conversion_tracking_ready: bool = True,
        confirmed_revenue_ready: bool = False,  # PM-3 / PM-4
        auto_recovery_ready: bool = True,
        certified_plugins_ready: bool = True,
        test_coverage_ready: bool = True,
        observability_ready: bool = True,
        reproducibility_ready: bool = True
    ) -> Dict[str, Any]:
        
        dimensions = {
            "auto_publishing": {"score": 10 if auto_publishing_ready else 0, "max": 10},
            "analytics_tracking": {"score": 10 if analytics_tracking_ready else 0, "max": 10},
            "conversion_tracking": {"score": 15 if conversion_tracking_ready else 0, "max": 15},
            "confirmed_revenue": {"score": 20 if confirmed_revenue_ready else 0, "max": 20},
            "auto_recovery": {"score": 10 if auto_recovery_ready else 0, "max": 10},
            "certified_plugins": {"score": 10 if certified_plugins_ready else 0, "max": 10},
            "test_coverage": {"score": 10 if test_coverage_ready else 0, "max": 10},
            "observability": {"score": 10 if observability_ready else 0, "max": 10},
            "reproducibility": {"score": 5 if reproducibility_ready else 0, "max": 5}
        }

        total_score = sum(d["score"] for d in dimensions.values())
        max_possible = sum(d["max"] for d in dimensions.values())

        if total_score >= 90:
            maturity_level = "PRODUCTION_SCALABLE"
        elif total_score >= 75:
            maturity_level = "LIVE_OPERATIONAL"
        elif total_score >= 50:
            maturity_level = "VALIDATED_FRAMEWORK"
        else:
            maturity_level = "EXPERIMENTAL"

        return {
            "pmi_score": total_score,
            "max_score": max_possible,
            "pmi_percentage": round((total_score / max_possible) * 100, 1),
            "maturity_level": maturity_level,
            "dimensions": dimensions
        }
