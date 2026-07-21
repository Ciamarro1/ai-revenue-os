import math
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from src.core.cognition.repository import CognitiveRepository
from src.core.events.event_bus import EventBus

class EvidenceEngine:
    """
    Evidence Intelligence Engine (Sprint 4).
    Analisa e avalia a qualidade das evidências coletadas pelo sistema
    para ajustar a taxa de aprendizado e mitigar o ruído experimental.
    """
    def __init__(self, repo: CognitiveRepository):
        self.repo = repo

    def calculate_quality_score(
        self,
        sample_size: int,
        statistical_confidence: float,
        reliability: float,
        timestamp_str: str
    ) -> Dict[str, float]:
        """
        Calcula os fatores individuais de qualidade e o escore final agregador.
        Retorna escore em [0.10, 1.0].
        """
        # 1. Fator de Tamanho da Amostra (Logarítmico)
        if sample_size <= 0:
            sample_size_factor = 0.10
        else:
            sample_size_factor = max(0.10, min(1.0, math.log10(sample_size + 1) / 5.0))
            
        # 2. Confiança Estatística (1.0 - p-value)
        if statistical_confidence is None or statistical_confidence < 0.0:
            stat_conf = 0.50
        else:
            stat_conf = max(0.0, min(1.0, statistical_confidence))
            
        # 3. Confiabilidade da Fonte
        rel_score = max(0.0, min(1.0, reliability))
        
        # 4. Fator de Recência (Decaimento linear em 30 dias)
        try:
            cleaned_ts = timestamp_str
            if cleaned_ts.endswith("Z"):
                cleaned_ts = cleaned_ts[:-1]
                # Se não contiver + ou - no offset de hora, adiciona +00:00
                if not ("+" in cleaned_ts or ("-" in cleaned_ts and cleaned_ts.rfind("-") > 10)):
                    cleaned_ts += "+00:00"
            ts = datetime.fromisoformat(cleaned_ts)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = now - ts
            days_elapsed = max(0.0, delta.total_seconds() / 86400.0)
            recency_factor = max(0.10, min(1.0, 1.0 - (days_elapsed / 30.0)))
        except Exception:
            recency_factor = 1.0
            
        # 5. Escore de Qualidade Agregado
        quality_score = sample_size_factor * stat_conf * rel_score * recency_factor
        quality_score = max(0.10, min(1.0, quality_score))
        
        return {
            "sample_size_factor": sample_size_factor,
            "statistical_confidence": stat_conf,
            "reliability": rel_score,
            "recency_factor": recency_factor,
            "quality_score": quality_score
        }

    def evaluate_evidence(
        self,
        evidence_id: int,
        sample_size: int,
        statistical_confidence: float,
        reliability: float
    ) -> float:
        """
        Busca a evidência no banco, calcula sua qualidade e persiste no SQLite.
        """
        # 1. Obter timestamp da evidência
        timestamp_str = None
        with self.repo._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT timestamp FROM evidence WHERE id = ?", (evidence_id,))
            row = c.fetchone()
            if row:
                timestamp_str = row[0]
                
        if not timestamp_str:
            timestamp_str = datetime.now(timezone.utc).isoformat() + "Z"
            
        # 2. Calcular escores de qualidade
        metrics = self.calculate_quality_score(
            sample_size=sample_size,
            statistical_confidence=statistical_confidence,
            reliability=reliability,
            timestamp_str=timestamp_str
        )
        
        # 3. Gravar na tabela evidence_quality
        with self.repo._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO evidence_quality (evidence_id, sample_size, confidence, reliability, recency, quality_score)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(evidence_id) DO UPDATE SET
                    sample_size=excluded.sample_size,
                    confidence=excluded.confidence,
                    reliability=excluded.reliability,
                    recency=excluded.recency,
                    quality_score=excluded.quality_score
            """, (
                evidence_id,
                sample_size,
                metrics["statistical_confidence"],
                metrics["reliability"],
                metrics["recency_factor"],
                metrics["quality_score"]
            ))
            conn.commit()
            
        # 4. Publicar evento no Cognitive Event Bus
        try:
            EventBus(self.repo.db).publish("EvidenceEvaluated", {
                "evidence_id": evidence_id,
                "sample_size": sample_size,
                "statistical_confidence": statistical_confidence,
                "reliability": reliability,
                "quality_score": metrics["quality_score"]
            })
        except Exception:
            pass

        # 5. Sincroniza síncronamente o Markdown de evidências
        self.repo.sync_evidence_markdown()
        
        return metrics["quality_score"]

