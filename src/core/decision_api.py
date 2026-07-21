from typing import Dict, Any, Optional
from src.core.cognition.repository import CognitiveRepository

class DecisionAPI:
    """
    Decision Facade API.
    Implementa a política de decisão baseada em Expected Value (Confiança * Qualidade * Impacto - Risco).
    """
    def __init__(self, repo: CognitiveRepository):
        self.repo = repo

    def evaluate_decision(
        self,
        belief_id: int,
        expected_impact: float,
        risk: float,
        default_quality: float = 0.80
    ) -> Dict[str, Any]:
        """
        Calcula o Decision Score e retorna a ação recomendada:
          - Decision Score = Belief Confidence * Evidence Quality * Expected Impact - Risk
          
        Recomendações:
          - Score >= 0.50: "EXECUTE" (Executar/Escalar)
          - 0.20 <= Score < 0.50: "TEST" (Testar/Iterar)
          - Score < 0.20: "IGNORE" (Ignorar/Encerrar)
        """
        # 1. Obter a crença
        with self.repo._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT confidence_score, statement FROM beliefs WHERE id = ?", (belief_id,))
            row = c.fetchone()
            
        if not row:
            raise ValueError(f"Crença com ID {belief_id} não existe.")
            
        belief_confidence = row[0]
        statement = row[1]

        # 2. Obter a qualidade da última evidência associada
        evidence_quality = default_quality
        with self.repo._get_conn() as conn:
            c = conn.cursor()
            # Busca a qualidade da evidência mais recente associada a esta crença (através da tabela evidence)
            c.execute("""
                SELECT eq.quality_score 
                FROM evidence_quality eq
                JOIN evidence e ON eq.evidence_id = e.id
                JOIN beliefs b ON b.statement LIKE '%' || e.claim || '%' OR e.hypothesis_id IS NOT NULL
                WHERE b.id = ?
                ORDER BY eq.id DESC LIMIT 1
            """, (belief_id,))
            eq_row = c.fetchone()
            if eq_row:
                evidence_quality = eq_row[0]

        # 3. Calcular score final
        decision_score = (belief_confidence * evidence_quality * expected_impact) - risk
        
        # 4. Determinar recomendação
        if decision_score >= 0.50:
            recommendation = "EXECUTE"
        elif decision_score >= 0.20:
            recommendation = "TEST"
        else:
            recommendation = "IGNORE"

        return {
            "belief_id": belief_id,
            "belief_statement": statement,
            "belief_confidence": belief_confidence,
            "evidence_quality": evidence_quality,
            "expected_impact": expected_impact,
            "risk": risk,
            "decision_score": round(decision_score, 4),
            "recommendation": recommendation
        }

