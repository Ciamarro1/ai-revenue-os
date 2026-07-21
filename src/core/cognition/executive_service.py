import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Callable

from src.core.cognition.models import Action, ActionDependency, ExecutionHistory, GraphNode, GraphEdge, Observation
from src.core.cognition.executive_repository import ExecutiveRepository
from src.core.cognition.planning_repository import PlanningRepository
from src.core.cognition.repository import CognitiveRepository

class ExecutiveService:
    """
    ExecutiveService (Sprint 7.0).
    Orquestra a execução de planos tácticos e passos do plano como ações operacionais complexas,
    gerenciando estado, retentativas (retries), dependências, idempotência e realimentando
    o Cognitive Kernel via novas observações e arestas do Evidence Graph.
    """
    def __init__(
        self,
        executive_repo: ExecutiveRepository,
        planning_repo: PlanningRepository,
        cognitive_repo: CognitiveRepository,
        db: Any
    ):
        self.executive_repo = executive_repo
        self.planning_repo = planning_repo
        self.cognitive_repo = cognitive_repo
        self.db = db

    def create_action_from_step(self, step_id: int) -> Action:
        step = self.planning_repo.get_plan_step(step_id)
        if not step:
            raise ValueError(f"Passo de plano {step_id} não encontrado.")

        action = Action(
            step_id=step_id,
            name=f"Ação: {step.action_description}",
            status="Pending"
        )
        saved_action = self.executive_repo.save_action(action)

        # Registrar nó da Ação no Grafo
        action_node_id = f"action:{saved_action.id}"
        self.cognitive_repo.save_node(GraphNode(
            id=action_node_id,
            type="action",
            label=saved_action.name[:50]
        ))

        # Aresta: Ação -> Passo do Plano ("executes")
        self.cognitive_repo.save_edge(GraphEdge(
            source=action_node_id,
            target=f"plan_step:{step_id}",
            relation_type="executes",
            weight=1.0
        ))

        return saved_action

    def execute_action(self, action_id: int, execution_callback: Optional[Callable[[], Any]] = None) -> bool:
        action = self.executive_repo.get_action(action_id)
        if not action:
            raise ValueError(f"Ação {action_id} não encontrada.")

        # 1. Idempotency Guard: Ações já completas ou canceladas não são reexecutadas
        if action.status == "Completed":
            return True
        if action.status == "Cancelled":
            return False

        # 2. Dependency Guard: Verifica dependências
        dep_ids = self.executive_repo.get_dependencies_for_action(action_id)
        for dep_id in dep_ids:
            dep_action = self.executive_repo.get_action(dep_id)
            if not dep_action or dep_action.status != "Completed":
                # Dependência não está pronta, pausa a execução
                action.status = "Paused"
                self.executive_repo.save_action(action)
                self.executive_repo.log_execution(action_id, "Paused", f"Aguardando conclusão da dependência {dep_id}")
                return False

        # 3. Iniciar Execução
        action.status = "Executing"
        self.executive_repo.save_action(action)
        self.executive_repo.log_execution(action_id, "Executing")

        # Registrar nó da Execução no Grafo
        exec_node_id = f"execution:{action_id}"
        self.cognitive_repo.save_node(GraphNode(
            id=exec_node_id,
            type="execution",
            label=f"Execução da Ação #{action_id}"
        ))

        # Aresta: Execução -> Ação ("runs")
        self.cognitive_repo.save_edge(GraphEdge(
            source=exec_node_id,
            target=f"action:{action_id}",
            relation_type="runs",
            weight=1.0
        ))

        try:
            # Executa a lógica
            if execution_callback:
                execution_callback()

            # Execução sucedeu
            action.status = "Completed"
            self.executive_repo.save_action(action)
            self.executive_repo.log_execution(action_id, "Completed")

            # 4. Emitir observação de volta no Cognitive Kernel
            obs = Observation(
                source="executive_engine",
                metric_name="ExecutionSuccess",
                value=1.0,
                raw_data=f"Resultado empírico da execução da ação: {action.name}"
            )
            saved_obs = self.cognitive_repo.save_observation(obs)

            # Aresta: Observação -> Ação ("verifies")
            self.cognitive_repo.save_edge(GraphEdge(
                source=f"observation:{saved_obs.id}",
                target=f"action:{action_id}",
                relation_type="verifies",
                weight=1.0
            ))

            return True

        except Exception as e:
            # Execução falhou: gerencia retentativas
            action.retry_count += 1
            error_msg = str(e)
            
            if action.retry_count < action.max_retries:
                action.status = "Pending" # Retorna para pendente para nova tentativa
                self.executive_repo.save_action(action)
                self.executive_repo.log_execution(action_id, "Retrying", f"Falha na tentativa {action.retry_count}: {error_msg}")
            else:
                action.status = "Failed"
                self.executive_repo.save_action(action)
                self.executive_repo.log_execution(action_id, "Failed", f"Limite de retentativas atingido: {error_msg}")
                
            return False

    def pause_action(self, action_id: int) -> None:
        action = self.executive_repo.get_action(action_id)
        if action:
            action.status = "Paused"
            self.executive_repo.save_action(action)
            self.executive_repo.log_execution(action_id, "Paused")

    def cancel_action(self, action_id: int) -> None:
        action = self.executive_repo.get_action(action_id)
        if action:
            action.status = "Cancelled"
            self.executive_repo.save_action(action)
            self.executive_repo.log_execution(action_id, "Cancelled")
