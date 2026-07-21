from typing import Dict, Any
from pydantic import BaseModel, Field
from src.reality.oss_catalog.catalog import OSSEntry

class OSSEvaluationResult(BaseModel):
    tool_name: str
    category: str
    overall_score: float  # 0.0 to 100.0
    recommendation: str  # RECOMMENDED_PRIMARY, RECOMMENDED_FALLBACK, REJECTED
    criteria_breakdown: Dict[str, bool]
    justification: str

class OSSEvaluationScorecard:
    """
    Mecanismo de Governança Tecnológica (Open Source Review V2).
    Avalia 8 critérios quantitativos antes de homologar qualquer ferramenta Open Source no AI Revenue OS.
    """

    def evaluate_entry(self, entry: OSSEntry) -> OSSEvaluationResult:
        criteria = {
            "maintained_recent": entry.last_commit_days_ago <= 90,
            "compatible_license": entry.license.upper() in ["MIT", "APACHE-2.0", "BSD", "BSD-3-CLAUSE", "AGPL-3.0", "FAIR-CODE"],
            "api_available": entry.api_available,
            "docker_ready": entry.docker_ready,
            "has_python_support": "PYTHON" in entry.language.upper() or "TS" in entry.language.upper() or "GO" in entry.language.upper(),
            "active_community": entry.stars >= 1000,
            "high_maintenance_score": entry.maintenance_score >= 0.75,
            "seamless_integration": entry.integration_ease.upper() in ["SEAMLESS", "MEDIUM"]
        }

        passed_count = sum(1 for v in criteria.values() if v)
        score = round((passed_count / len(criteria)) * 100.0, 1)

        if score >= 80.0:
            rec = "RECOMMENDED_PRIMARY"
            justification = f"Ferramenta '{entry.name}' passou com {score}% de aprovação em governança. Homologada como Provedor Primário."
        elif score >= 60.0:
            rec = "RECOMMENDED_FALLBACK"
            justification = f"Ferramenta '{entry.name}' atingiu {score}%. Homologada como Provedor Secundário/Fallback."
        else:
            rec = "REJECTED"
            justification = f"Ferramenta '{entry.name}' atingiu apenas {score}%. Rejeitada por riscos de governança ou descontinuidade."

        return OSSEvaluationResult(
            tool_name=entry.name,
            category=entry.category,
            overall_score=score,
            recommendation=rec,
            criteria_breakdown=criteria,
            justification=justification
        )
