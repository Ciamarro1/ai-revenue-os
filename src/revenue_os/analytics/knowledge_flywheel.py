import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class KnowledgeFlywheel:
    """
    Knowledge Flywheel (Sprint 7.6).
    Mecanismo de retroalimentação contínua de aprendizado.
    Converte resultados de receita e analytics em regras e insights na Knowledge Base.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            self.storage_path = Path(__file__).parent.parent.parent.parent / "knowledge" / "knowledge_flywheel.json"
        else:
            self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.insights = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if not self.storage_path.exists():
            return self._default_baseline_insights()
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self._default_baseline_insights()

    def _default_baseline_insights(self) -> List[Dict[str, Any]]:
        return [
            {"category": "format", "niche": "general", "platform": "pinterest", "rule": "Imagens claras de alta resolução aumentam CTR em +18%", "confidence": 0.92, "impact": "+18% CTR"},
            {"category": "video_length", "niche": "general", "platform": "pinterest", "rule": "Vídeos curtos de 15 segundos aumentam a retenção em +31%", "confidence": 0.89, "impact": "+31% Retenção"},
            {"category": "timing", "niche": "recipes", "platform": "pinterest", "rule": "Conteúdo de receitas de cozinha performam 2.4x melhor aos domingos", "confidence": 0.85, "impact": "2.4x Engajamento"},
            {"category": "hook", "niche": "finance", "platform": "pinterest", "rule": "Gancho inicial 'Você sabia?' eleva CTR em +11%", "confidence": 0.87, "impact": "+11% CTR"},
            {"category": "color", "niche": "lifestyle", "platform": "pinterest", "rule": "Tons predominantemente verdes e neutros aumentam Save Rate em +6%", "confidence": 0.84, "impact": "+6% Save Rate"}
        ]

    def ingest_experiment_learning(self, experiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consome um experimento concluído e extrai novas regras e aprendizados.
        """
        ctr = experiment_data.get("ctr", 0.0)
        revenue = experiment_data.get("revenue", 0.0)
        niche = experiment_data.get("niche", "general")
        platform = experiment_data.get("platform", "pinterest")
        hook = experiment_data.get("hook", "Standard")

        insight = {
            "category": "experiment_result",
            "niche": niche,
            "platform": platform,
            "hook": hook,
            "rule": f"Hook '{hook}' no nicho '{niche}' gerou CTR de {ctr*100:.1f}% e ${revenue:.2f} de receita",
            "confidence": 0.90 if revenue > 0 else 0.70,
            "impact": f"${revenue:.2f} Revenue",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
        }

        self.insights.append(insight)
        self.save()
        return insight

    def save(self) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.insights, f, indent=2, ensure_ascii=False)

    def get_actionable_insights(self, niche: Optional[str] = None, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for item in self.insights:
            if niche and item.get("niche") not in (niche, "general"):
                continue
            if platform and item.get("platform") not in (platform, "all"):
                continue
            results.append(item)
        return results
