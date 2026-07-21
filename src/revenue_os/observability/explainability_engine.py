import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class ExplainabilityEngine:
    """
    Explainability Engine do AI Revenue OS (Sprint 13).
    Gera registros de auditoria explicáveis para cada decisão tomada pelo sistema,
    detalhando os fatores numéricos, desvios e justificativas racionais.
    """

    def __init__(self, log_path: Optional[Path] = None):
        if log_path is None:
            self.log_path = Path(__file__).parent.parent.parent.parent / "knowledge" / "decision_explanations.jsonl"
        else:
            self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def explain_niche_selection(self, niche: str, expected_ctr_gain: float, competition_reduction: float, commission_gain: float, confidence: float, projected_roi: float) -> Dict[str, Any]:
        explanation = (
            f"Nicho '{niche}' selecionado porque apresenta CTR esperado {expected_ctr_gain*100:+.1f}%, "
            f"Competição {competition_reduction*100:+.1f}%, Comissão {commission_gain*100:+.1f}%, "
            f"Confiança de {confidence*100:.0f}% e ROI previsto de {projected_roi:.1f}x."
        )

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "action": "SELECT_NICHE",
            "target": niche,
            "explanation": explanation,
            "factors": {
                "expected_ctr_gain_percent": round(expected_ctr_gain * 100, 1),
                "competition_reduction_percent": round(competition_reduction * 100, 1),
                "commission_gain_percent": round(commission_gain * 100, 1),
                "confidence_score": confidence,
                "projected_roi": projected_roi
            }
        }
        self._append_log(record)
        return record

    def explain_resource_allocation(self, experiment_id: str, action: str, reason: str, confidence: float) -> Dict[str, Any]:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "action": f"ALLOCATE_RESOURCE_{action}",
            "target": experiment_id,
            "explanation": f"Decisão de {action} para experimento '{experiment_id}': {reason}.",
            "factors": {
                "confidence": confidence
            }
        }
        self._append_log(record)
        return record

    def generate_decision_dag(self, asset_id: str, opportunity_id: str, genome_id: str, experiment_id: str, revenue: float) -> Dict[str, Any]:
        """
        Reconstrói a árvore causal de decisão (DAG Lineage Trace):
        Research ➔ Opportunity ➔ Genome ➔ Experiment ➔ Allocation ➔ Revenue.
        """
        dag_dir = self.log_path.parent / "decision_dags"
        dag_dir.mkdir(parents=True, exist_ok=True)

        dag = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "business_asset_id": asset_id,
            "nodes": [
                {"id": "node_1", "step": "RESEARCH", "target": "Market Discovery"},
                {"id": "node_2", "step": "OPPORTUNITY", "target": opportunity_id},
                {"id": "node_3", "step": "GENOME", "target": genome_id},
                {"id": "node_4", "step": "EXPERIMENT", "target": experiment_id},
                {"id": "node_5", "step": "ALLOCATION", "target": "Portfolio Manager"},
                {"id": "node_6", "step": "REVENUE", "target": f"${revenue:.2f} USD"}
            ],
            "edges": [
                ("node_1", "node_2"),
                ("node_2", "node_3"),
                ("node_3", "node_4"),
                ("node_4", "node_5"),
                ("node_5", "node_6")
            ],
            "status": "PROVEN" if revenue > 0 else "EVALUATING"
        }

        filepath = dag_dir / f"dag_{asset_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dag, f, indent=2, ensure_ascii=False)

        return dag

    def _append_log(self, record: Dict[str, Any]) -> None:
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
