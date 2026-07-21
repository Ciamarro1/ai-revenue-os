import logging
from typing import Optional
from datetime import datetime, timezone
from src.core.cognition.models import Observation, Evidence, Belief, GraphNode, GraphEdge
from src.core.cognition.repository import CognitiveRepository
from src.core.cognition.belief_manager import BeliefManager

logger = logging.getLogger(__name__)

class BeliefService:
    """
    Belief Service (Sprint 6.0).
    Orchestrates the cognitive pipeline:
    Observation -> Evidence -> Belief -> Confidence -> Revision.
    """
    def __init__(self, repo: CognitiveRepository, belief_manager: BeliefManager):
        self.repo = repo
        self.belief_manager = belief_manager

    def process_observation(
        self,
        observation: Observation,
        related_belief_id: int,
        baseline_value: float = 1.0,
        tolerance_percent: float = 10.0,
        experiment_id: Optional[str] = None
    ) -> Evidence:
        """
        Processes a raw observation, evaluates its statistical impact,
        transforms it into empirical evidence, and revises the corresponding system belief.
        Also structures the trace links in the Evidence Graph.
        """
        logger.info(f"Processing raw observation from source: {observation.source}")
        
        # 1. Persistir a observacão no banco e registrar no grafo
        saved_obs = self.repo.save_observation(observation)
        obs_node_id = f"observation:{saved_obs.id}"
        self.repo.save_node(GraphNode(
            id=obs_node_id,
            type="observation",
            label=f"Obs {saved_obs.id}: {observation.metric_name} = {observation.value}"
        ))
        
        # 2. Confidence scoring (cálculo de escore da evidência)
        source_reliability = 0.85 if observation.source.endswith("scraper") else 0.95
        evidence_confidence = min(1.0, max(0.0, source_reliability))
        
        # 3. Determinar o impacto (Positivo, Negativo ou Neutro) baseando-se em limites/baseline
        upper_limit = baseline_value * (1.0 + (tolerance_percent / 100.0))
        lower_limit = baseline_value * (1.0 - (tolerance_percent / 100.0))
        
        if observation.value > upper_limit:
            impact = "positivo"
            claim = f"Métrica {observation.metric_name} ({observation.value}) superou o baseline de {baseline_value}."
        elif observation.value < lower_limit:
            impact = "negativo"
            claim = f"Métrica {observation.metric_name} ({observation.value}) ficou abaixo do baseline de {baseline_value}."
        else:
            impact = "neutro"
            claim = f"Métrica {observation.metric_name} ({observation.value}) permaneceu dentro da faixa de tolerância do baseline."
 
        # 4. Criar e registrar a Evidência no banco e no grafo
        evidence = Evidence(
            hypothesis_id=None,
            experiment_id=experiment_id or f"OBS-{saved_obs.id}",
            claim=claim,
            confidence_score=evidence_confidence,
            impact=impact,
            timestamp=datetime.now(timezone.utc).isoformat() + "Z",
            narrative=f"Observado automaticamente via {observation.source}. Dados brutos: {observation.raw_data or 'N/A'}"
        )
        registered_evidence = self.repo.register_evidence(evidence)
        ev_node_id = f"evidence:{registered_evidence.id}"
        self.repo.save_node(GraphNode(
            id=ev_node_id,
            type="evidence",
            label=f"Ev {registered_evidence.id}: {registered_evidence.impact}"
        ))
        
        # Relacionar Observação -> Evidência
        self.repo.save_edge(GraphEdge(
            source=obs_node_id,
            target=ev_node_id,
            relation_type="originates",
            weight=1.0
        ))
        
        # 5. Belief Revision (evoluir e revisar a crença relacionada)
        reason = f"Nova observacão de {observation.source}: {claim}"
        self.belief_manager.evolve_belief(
            belief_id=related_belief_id,
            evidence_confidence=evidence_confidence,
            impact=impact,
            reason=reason,
            quality_score=0.9
        )
        
        belief_node_id = f"belief:{related_belief_id}"
        belief_obj = self.repo.get_beliefs()
        belief = next((b for b in belief_obj if b.id == related_belief_id), None)
        belief_label = belief.statement if belief else f"Belief {related_belief_id}"
        
        self.repo.save_node(GraphNode(
            id=belief_node_id,
            type="belief",
            label=belief_label,
            properties={"confidence_score": belief.confidence_score if belief else 0.5}
        ))
        
        # Relacionar Evidência -> Crença
        self.repo.save_edge(GraphEdge(
            source=ev_node_id,
            target=belief_node_id,
            relation_type="supports" if registered_evidence.impact == "positivo" else ("modifies" if registered_evidence.impact == "negativo" else "touches"),
            weight=evidence_confidence
        ))
        
        # Se associado a experimento, registrar nós e arestas do experimento
        exp_id = registered_evidence.experiment_id
        if exp_id:
            exp_node_id = f"experiment:{exp_id}"
            self.repo.save_node(GraphNode(
                id=exp_node_id,
                type="experiment",
                label=f"Experiment {exp_id}"
            ))
            self.repo.save_edge(GraphEdge(
                source=exp_node_id,
                target=obs_node_id,
                relation_type="triggers"
            ))
            self.repo.save_edge(GraphEdge(
                source=exp_node_id,
                target=belief_node_id,
                relation_type="modifies"
            ))
        
        logger.info(f"Belief {related_belief_id} revised successfully based on Evidence E-{registered_evidence.id}.")
        return registered_evidence
