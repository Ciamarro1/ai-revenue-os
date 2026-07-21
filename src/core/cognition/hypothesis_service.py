import logging
from datetime import datetime, timezone
from typing import Optional, List
from src.core.cognition.models import Hypothesis, GraphNode, GraphEdge
from src.core.cognition.hypothesis_repository import HypothesisRepository
from src.core.cognition.repository import CognitiveRepository

logger = logging.getLogger(__name__)

class HypothesisService:
    """
    HypothesisService (Sprint 6.2).
    Orchestrates the scientific reasoning engine:
    - Bayesian confidence scoring of hypotheses.
    - Manages supporting/contradicting evidence links.
    - Integrates links into the Evidence Graph.
    - Handles promotion of validated hypotheses into Experiments.
    """
    def __init__(self, hypothesis_repo: HypothesisRepository, cognitive_repo: CognitiveRepository):
        self.hypothesis_repo = hypothesis_repo
        self.cognitive_repo = cognitive_repo

    def create_hypothesis(self, statement: str, initial_confidence: float = 0.50) -> Hypothesis:
        """Cria e registra uma nova hipótese proposta."""
        hypothesis = Hypothesis(
            statement=statement,
            confidence_score=initial_confidence,
            status="Proposed"
        )
        saved = self.hypothesis_repo.save_hypothesis(hypothesis)
        
        # Registrar o nó no Grafo de Evidências
        self.cognitive_repo.save_node(GraphNode(
            id=f"hypothesis:{saved.id}",
            type="hypothesis",
            label=f"Hypothesis: {saved.statement}",
            properties={"confidence": saved.confidence_score, "status": saved.status}
        ))
        return saved

    def evaluate_evidence(
        self,
        hypothesis_id: int,
        evidence_id: int,
        is_supporting: bool,
        learning_rate: float = 0.15
    ) -> float:
        """
        Aplica atualização Bayesiana de confiança na hipótese baseado em nova evidência.
        Conecta a evidência à hipótese no Grafo de Evidências com relação de suporte ou contradição.
        """
        hyp = self.hypothesis_repo.get_hypothesis(hypothesis_id)
        if not hyp:
            raise ValueError(f"Hipótese {hypothesis_id} não encontrada.")

        # Obter dados da evidência para obter a confiança da evidência
        # Usamos CognitiveRepository para obter a evidência
        # Mas para testes/robustez, caso não ache, usamos 1.0 como fallback
        evidence_confidence = 0.8
        with self.cognitive_repo._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT confidence_score FROM evidence WHERE id = ?", (evidence_id,))
            row = c.fetchone()
            if row:
                evidence_confidence = row[0]

        prior = hyp.confidence_score

        # Lógica de atualização Bayesiana simplificada:
        # Se suporta: P(H|E) = P(H) + (1 - P(H)) * P(E) * lr
        # Se contradiz: P(H|E) = P(H) - P(H) * P(E) * lr
        if is_supporting:
            posterior = prior + (1.0 - prior) * evidence_confidence * learning_rate
            relation = "supports"
        else:
            posterior = prior - prior * evidence_confidence * learning_rate
            relation = "contradicts"

        # Garantir limites matemáticos [0.0, 1.0]
        posterior = min(1.0, max(0.0, posterior))

        # Atualizar a hipótese no banco
        hyp.confidence_score = posterior
        
        # Transição de status baseado na confiança acumulada
        if posterior >= 0.85:
            hyp.status = "Validated"
        elif posterior <= 0.15:
            hyp.status = "Rejected"
        else:
            hyp.status = "Proposed"

        self.hypothesis_repo.save_hypothesis(hyp)

        # Salvar/atualizar nó da hipótese no grafo
        self.cognitive_repo.save_node(GraphNode(
            id=f"hypothesis:{hyp.id}",
            type="hypothesis",
            label=f"Hypothesis: {hyp.statement}",
            properties={"confidence": hyp.confidence_score, "status": hyp.status}
        ))

        # Salvar/atualizar nó da evidência no grafo
        self.cognitive_repo.save_node(GraphNode(
            id=f"evidence:{evidence_id}",
            type="evidence",
            label=f"Evidence {evidence_id}"
        ))

        # Conectar evidência à hipótese no grafo
        self.cognitive_repo.save_edge(GraphEdge(
            source=f"evidence:{evidence_id}",
            target=f"hypothesis:{hyp.id}",
            relation_type=relation,
            weight=evidence_confidence
        ))

        logger.info(f"Hypothesis {hypothesis_id} evaluated with Evidence {evidence_id}. New confidence: {posterior:.4f} ({hyp.status})")
        return posterior

    def promote_to_experiment(self, hypothesis_id: int) -> str:
        """
        Promove uma hipótese validada para um experimento ativo no ecossistema.
        Registra no banco de experimentos e cria a conexão causal no Grafo de Evidências.
        """
        hyp = self.hypothesis_repo.get_hypothesis(hypothesis_id)
        if not hyp:
            raise ValueError(f"Hipótese {hypothesis_id} não encontrada.")

        # Gerar ID único para o experimento científico
        experiment_id = f"EXP-HYP-{hyp.id}"
        ts = datetime.now(timezone.utc).isoformat() + "Z"

        # Cadastrar o experimento na tabela de experimentos do motor
        # Tabela: experiments (id, hypothesis_id, status, budget_limit, etc.)
        # Vamos verificar se a tabela experiments existe e inserir nela
        with self.cognitive_repo._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO experiments (experiment_id, hypothesis_id, status, published_at)
                VALUES (?, ?, ?, ?)
            """, (experiment_id, hyp.id, "created", ts))
            conn.commit()

        # Atualizar status da hipótese para indicar que foi promovida
        hyp.status = "Validated"
        self.hypothesis_repo.save_hypothesis(hyp)

        # Atualizar nó da hipótese no grafo
        self.cognitive_repo.save_node(GraphNode(
            id=f"hypothesis:{hyp.id}",
            type="hypothesis",
            label=f"Hypothesis: {hyp.statement}",
            properties={"confidence": hyp.confidence_score, "status": hyp.status}
        ))

        # Criar nó do experimento no grafo
        self.cognitive_repo.save_node(GraphNode(
            id=f"experiment:{experiment_id}",
            type="experiment",
            label=f"Experiment: {experiment_id}"
        ))

        # Criar aresta no grafo conectando o Experimento para testar a Hipótese
        self.cognitive_repo.save_edge(GraphEdge(
            source=f"experiment:{experiment_id}",
            target=f"hypothesis:{hyp.id}",
            relation_type="tests",
            weight=1.0
        ))

        logger.info(f"Hypothesis {hypothesis_id} promoted to Experiment {experiment_id} successfully.")
        return experiment_id
