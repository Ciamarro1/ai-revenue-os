from typing import List, Optional, Callable, Any, Dict
from src.core.cognition.tool_repository import ToolRepository
from src.core.cognition.tool_service import ToolRegistryService
from src.core.cognition.models import Provider, Tool, Capability, ToolExecution

class ToolAPI:
    """
    ToolAPI Facade (Sprint 7.1).
    Isola a descoberta, benchmarking e instrumentação do Capability System.
    """
    def __init__(self, repository: ToolRepository, service: ToolRegistryService):
        self.repository = repository
        self.service = service

    def register(self, provider: Provider, tool: Tool, cap: Capability) -> Tool:
        """Registra um provedor, uma capacidade e uma ferramenta no sistema."""
        return self.service.register_capability_system(provider, tool, cap)

    def select_tool(self, cap_name: str) -> Optional[Tool]:
        """Seleciona a ferramenta ideal com base em métricas de latência/custo/saúde."""
        return self.service.select_optimal_tool_for_capability(cap_name)

    def execute(
        self,
        tool_id: int,
        action_id: int,
        execution_fn: Callable[[], Any],
        cost: float = 0.0
    ) -> Dict[str, Any]:
        """Executa a lógica da ferramenta com monitoramento de latência e telemetria."""
        return self.service.execute_tool(tool_id, action_id, execution_fn, cost)

    def get_providers(self) -> List[Provider]:
        """Busca todos os provedores."""
        return self.repository.get_providers()

    def get_tools(self) -> List[Tool]:
        """Busca todas as ferramentas."""
        return self.repository.get_tools()

    def get_capabilities(self) -> List[Capability]:
        """Busca todas as capacidades mapeadas."""
        return self.repository.get_capabilities()

    def get_tool_executions(self, tool_id: int) -> List[ToolExecution]:
        """Busca todo o histórico de execuções de uma ferramenta."""
        return self.repository.get_tool_executions(tool_id)
