from datetime import datetime, timezone
from typing import Optional, Any
from src.core.cognition.repository import CognitiveRepository
from src.core.cognition.models import Belief
from src.core.events.event_bus import EventBus

class BeliefManager:
    """
    Belief Evolution Engine (Sprint 3).
    Ajusta dinamicamente a confiança das crenças do sistema com base em evidências experimentais.
    Regista a trajetória histórica de mudanças de confiança em SQLite.
    """
    def __init__(self, repo: CognitiveRepository):
        self.repo = repo

    def evolve_belief(
        self,
        belief_id: int,
        evidence_confidence: float,
        impact: str,
        reason: str,
        learning_rate: float = 0.10,
        quality_score: float = 1.0
    ) -> float:
        """
        Ajusta a confiança de uma crença utilizando regras matemáticas síncronas.
        
        Regras:
        - Impacto Positivo: Confiança aumenta
        - Impacto Negativo: Confiança diminui
        - Impacto Neutro: Confiança inalterada
        """
        # 1. Recuperar a crença pelo ID
        beliefs = self.repo.get_beliefs()
        belief = next((b for b in beliefs if b.id == belief_id), None)
        if not belief:
            raise ValueError(f"Crença com ID {belief_id} não encontrada no banco.")
            
        old_confidence = belief.confidence_score
        
        # 2. Calcular nova confiança baseando-se no impacto e qualidade da evidência
        adjusted_lr = learning_rate * quality_score
        impact_normalized = impact.strip().lower()
        if impact_normalized in ["positivo", "positive"]:
            new_confidence = old_confidence + adjusted_lr * (1.0 - old_confidence) * evidence_confidence
        elif impact_normalized in ["negativo", "negative"]:
            new_confidence = old_confidence - adjusted_lr * old_confidence * evidence_confidence
        else:
            new_confidence = old_confidence
            
        # Clampar entre 0.0 e 1.0 para manter limites de probabilidade válidos
        new_confidence = max(0.0, min(1.0, new_confidence))
        
        # 3. Salvar crença atualizada
        belief.confidence_score = new_confidence
        self.repo.save_belief(belief)
        
        # 4. Gravar histórico na tabela belief_history
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self.repo._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO belief_history (belief_id, old_confidence, new_confidence, change_reason, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (belief_id, old_confidence, new_confidence, reason, ts))
            conn.commit()
            
        # 5. Publicar evento no Cognitive Event Bus
        try:
            EventBus(self.repo.db).publish("BeliefUpdated", {
                "belief_id": belief_id,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
                "reason": reason
            })
        except Exception:
            pass

        # 6. Forçar sincronização do Markdown
        self.repo.sync_beliefs_markdown()
        
        return new_confidence

