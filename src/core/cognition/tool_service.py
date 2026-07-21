import sqlite3
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Callable

from src.core.cognition.models import Provider, Tool, Capability, ToolExecution, GraphNode, GraphEdge
from src.core.cognition.tool_repository import ToolRepository
from src.core.cognition.repository import CognitiveRepository

class ToolRegistryService:
    """
    ToolRegistryService (Sprint 7.1).
    Orquestra a descoberta, seleção multi-provedor (multi-objective benchmark) e execução
    instrumentada de ferramentas externas, mantendo sincronia no Grafo de Evidências.
    """
    def __init__(
        self,
        tool_repo: ToolRepository,
        cognitive_repo: CognitiveRepository,
        db: Any
    ):
        self.tool_repo = tool_repo
        self.cognitive_repo = cognitive_repo
        self.db = db

    def register_capability_system(self, provider: Provider, tool: Tool, cap: Capability) -> Tool:
        # 1. Persistir entidades
        saved_provider = self.tool_repo.save_provider(provider)
        saved_cap = self.tool_repo.save_capability(cap)
        
        tool.provider_id = saved_provider.id
        # Garante que a capacidade esteja descrita nas tags da ferramenta
        caps_list = [c.strip() for c in tool.capabilities.split(",") if c.strip()]
        if saved_cap.name not in caps_list:
            caps_list.append(saved_cap.name)
        tool.capabilities = ", ".join(caps_list)
        
        saved_tool = self.tool_repo.save_tool(tool)

        # 2. Registrar nós no Grafo
        provider_node_id = f"provider:{saved_provider.id}"
        tool_node_id = f"tool:{saved_tool.id}"
        cap_node_id = f"capability:{saved_cap.id}"

        self.cognitive_repo.save_node(GraphNode(id=provider_node_id, type="provider", label=saved_provider.name))
        self.cognitive_repo.save_node(GraphNode(id=tool_node_id, type="tool", label=saved_tool.name))
        self.cognitive_repo.save_node(GraphNode(id=cap_node_id, type="capability", label=saved_cap.name))

        # 3. Registrar arestas
        # Ferramenta -> Capacidade ("implements")
        self.cognitive_repo.save_edge(GraphEdge(
            source=tool_node_id,
            target=cap_node_id,
            relation_type="implements",
            weight=1.0
        ))
        # Ferramenta -> Provedor ("provided_by")
        self.cognitive_repo.save_edge(GraphEdge(
            source=tool_node_id,
            target=provider_node_id,
            relation_type="provided_by",
            weight=1.0
        ))

        return saved_tool

    def select_optimal_tool_for_capability(self, cap_name: str) -> Optional[Tool]:
        tools = self.tool_repo.get_tools_by_capability(cap_name)
        if not tools:
            return None

        # Multi-objective utility:
        # Queremos maximizar confiabilidade e saúde física (health_score)
        # Queremos minimizar latência e custo unitário
        best_tool = None
        best_utility = -1.0

        for t in tools:
            reliability_score = max(0.01, t.reliability)
            health = max(0.01, t.health_score)
            cost_factor = max(0.01, t.cost)
            latency_factor = max(0.1, t.latency)

            # Fórmula composto de utilidade
            utility = (reliability_score * health) / (cost_factor * latency_factor)
            if utility > best_utility:
                best_utility = utility
                best_tool = t

        return best_tool

    def execute_tool(
        self,
        tool_id: int,
        action_id: int,
        execution_fn: Callable[[], Any],
        cost: float = 0.0
    ) -> Dict[str, Any]:
        tool = self.tool_repo.get_tool(tool_id)
        if not tool:
            raise ValueError(f"Ferramenta {tool_id} não cadastrada.")

        start_time = time.perf_counter()
        success = False
        error_msg = None
        result = None

        try:
            result = execution_fn()
            success = True
        except Exception as e:
            error_msg = str(e)
            raise e
        finally:
            elapsed = time.perf_counter() - start_time
            
            # Logar execução
            exec_log = ToolExecution(
                tool_id=tool_id,
                latency=elapsed,
                cost=cost,
                success=success,
                error_message=error_msg
            )
            saved_exec = self.tool_repo.log_tool_execution(exec_log)

            # Registrar nó da execução e arestas no Grafo
            exec_node_id = f"tool_execution:{saved_exec.id}"
            self.cognitive_repo.save_node(GraphNode(
                id=exec_node_id,
                type="tool_execution",
                label=f"Exec tool {tool.name[:20]} ({'OK' if success else 'FAIL'})"
            ))

            # Execução -> Ferramenta ("runs")
            self.cognitive_repo.save_edge(GraphEdge(
                source=exec_node_id,
                target=f"tool:{tool_id}",
                relation_type="runs",
                weight=1.0
            ))

            # Ação Executiva -> Execução de Ferramenta ("invokes")
            self.cognitive_repo.save_edge(GraphEdge(
                source=f"action:{action_id}",
                target=exec_node_id,
                relation_type="invokes",
                weight=1.0
            ))

        return {
            "success": success,
            "latency": elapsed,
            "result": result,
            "error": error_msg
        }
