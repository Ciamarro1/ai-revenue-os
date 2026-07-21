from abc import ABC, abstractmethod
from typing import Dict, Any

class AgentPort(ABC):
    """
    Agent Port interface.
    Decouples Agent multi-agent graph routers (LangGraph, CrewAI, AutoGen).
    """
    @abstractmethod
    def run_agent_cycle(self, task_description: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executa um ciclo completo de tomada de decisão do conselho de agentes."""
        pass
