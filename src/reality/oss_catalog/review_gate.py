import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from src.reality.oss_catalog.catalog import OSSCatalogService, OSSEntry

class OpenSourceReviewGate:
    """
    Open Source Review Gate (Princípio Open Source First).
    Força a validação obrigatória antes de qualquer implementação de nova funcionalidade:
    Se existe solução Open Source madura -> Integrar e criar Adapter.
    Se não existe -> Autorizar desenvolvimento proprietário do diferencial.
    """

    def __init__(self, review_log_path: Optional[Path] = None):
        if review_log_path is None:
            self.review_log_path = Path(__file__).parent.parent.parent.parent / "knowledge" / "oss_reviews.json"
        else:
            self.review_log_path = Path(review_log_path)
        self.review_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.catalog = OSSCatalogService()

    def review_feature_request(self, feature_name: str, category: str, problem_description: str) -> Dict[str, Any]:
        """
        Executa a revisão formal Open Source para a solicitação de funcionalidade.
        """
        candidates = self.catalog.search_solution(category=category, problem_description=problem_description)

        if candidates:
            selected_oss = candidates[0]
            decision = {
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "feature_name": feature_name,
                "category": category,
                "oss_available": True,
                "action": "INTEGRATE_AND_BUILD_ADAPTER",
                "selected_oss": selected_oss.name,
                "license": selected_oss.license,
                "official_url": selected_oss.official_url,
                "recommendation": f"NÃO desenvolver do zero. Utilizar '{selected_oss.name}' e criar um Adapter isolado."
            }
        else:
            decision = {
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "feature_name": feature_name,
                "category": category,
                "oss_available": False,
                "action": "DEVELOP_PROPRIETARY_DIFFERENTIATOR",
                "selected_oss": None,
                "recommendation": f"Nenhum projeto Open Source maduro encontrado para a categoria '{category}'. Desenvolvimento proprietário do diferencial AUTORIZADO."
            }

        self._log_review(decision)
        return decision

    def _log_review(self, decision: Dict[str, Any]) -> None:
        reviews = []
        if self.review_log_path.exists():
            try:
                with open(self.review_log_path, "r", encoding="utf-8") as f:
                    reviews = json.load(f)
            except Exception:
                reviews = []

        reviews.append(decision)
        with open(self.review_log_path, "w", encoding="utf-8") as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)
