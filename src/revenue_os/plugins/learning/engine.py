import os
import json
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from src.revenue_os.plugins.learning.models import (
    LearningConfig,
    HypothesisState,
    EconomicBrainWeight,
    LearningCycleResult
)

class ProductionLearningEngine:
    """
    Motor de Aprendizado e Recalibração de Produção (Sprint O8).
    Garante que SOMENTE evidências com proveniência REAL_PRODUCTION alterem os pesos do EconomicBrain.
    Simulações e Benchmarks são estritamente ignorados para fins de atualização de pesos.
    """

    def __init__(self, config: Optional[LearningConfig] = None):
        self.config = config or LearningConfig()
        self._hypotheses: Dict[str, HypothesisState] = {
            "HYP-01": HypothesisState(
                hypothesis_id="HYP-01",
                statement="Landing pages com vídeos 9:16 convertem 25% mais em ofertas de afiliado",
                prior_confidence=0.50,
                current_confidence=0.50
            ),
            "HYP-02": HypothesisState(
                hypothesis_id="HYP-02",
                statement="Pins com headlines determinísticas geram CTR 30% maior no Pinterest",
                prior_confidence=0.50,
                current_confidence=0.50
            )
        }
        self._weights: Dict[str, EconomicBrainWeight] = {
            "conversion_rate_prior": EconomicBrainWeight(
                param_name="conversion_rate_prior",
                current_weight=0.035,
                previous_weight=0.035,
                delta=0.0
            ),
            "expected_roi_multiplier": EconomicBrainWeight(
                param_name="expected_roi_multiplier",
                current_weight=1.50,
                previous_weight=1.50,
                delta=0.0
            )
        }

    def load_ledger_entries(self) -> List[Dict[str, Any]]:
        ledger_path = self.config.ledger_file_path
        if not os.path.exists(ledger_path):
            return []

        entries = []
        try:
            with open(ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        except Exception as e:
            logging.error(f"[LearningEngine] Erro ao ler {ledger_path}: {e}")
        return entries

    def run_cycle(self, custom_entries: Optional[List[Dict[str, Any]]] = None) -> LearningCycleResult:
        entries = custom_entries if custom_entries is not None else self.load_ledger_entries()
        total_entries = len(entries)

        # Filtro Absoluto EDD: SOMENTE REAL_PRODUCTION é aceito para aprendizado
        real_prod_entries = []
        benchmark_entries = []

        for e in entries:
            m_source = e.get("metric_source") or e.get("classification_status") or e.get("provenance", {}).get("provenance_type")
            if m_source == "REAL_PRODUCTION":
                real_prod_entries.append(e)
            else:
                benchmark_entries.append(e)

        promoted_count = 0
        rejected_count = 0
        weights_recalibrated = 0

        # Atualização de Hipóteses com dados de Produção Real
        if real_prod_entries:
            for hyp_id, hyp in self._hypotheses.items():
                hyp.sample_size += len(real_prod_entries)
                hyp.last_evidence_provenance = "REAL_PRODUCTION"

                # Bayes Update
                learning_factor = self.config.learning_rate * (len(real_prod_entries) / (hyp.sample_size + 10))
                hyp.current_confidence = min(0.99, max(0.01, hyp.current_confidence + learning_factor))

                # Promoção / Rejeição
                if hyp.current_confidence >= self.config.promotion_threshold and hyp.status != "PROMOTED_LAW":
                    hyp.status = "PROMOTED_LAW"
                    promoted_count += 1
                elif hyp.current_confidence <= self.config.rejection_threshold and hyp.status != "REJECTED":
                    hyp.status = "REJECTED"
                    rejected_count += 1

            # Recalibração de Pesos do EconomicBrain
            for param_name, weight in self._weights.items():
                weight.previous_weight = weight.current_weight
                weight.sample_size += len(real_prod_entries)
                
                # Ajuste positivo sutil sob confirmação de produção real
                delta = round(0.005 * len(real_prod_entries), 4)
                weight.current_weight = round(weight.current_weight + delta, 4)
                weight.delta = delta
                weight.updated_at = datetime.now(timezone.utc).isoformat() + "Z"
                weights_recalibrated += 1

        cycle_id = f"CYCLE-{uuid.uuid4().hex[:8].upper()}"
        ds_version = f"{self.config.dataset_version_prefix}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}"

        return LearningCycleResult(
            cycle_id=cycle_id,
            total_ledger_entries=total_entries,
            real_production_entries=len(real_prod_entries),
            ignored_benchmark_entries=len(benchmark_entries),
            hypotheses_evaluated=len(self._hypotheses),
            promoted_count=promoted_count,
            rejected_count=rejected_count,
            weights_recalibrated=weights_recalibrated,
            dataset_version=ds_version
        )

    def get_hypotheses(self) -> List[Dict[str, Any]]:
        return [h.model_dump() for h in self._hypotheses.values()]

    def get_weights(self) -> List[Dict[str, Any]]:
        return [w.model_dump() for w in self._weights.values()]
