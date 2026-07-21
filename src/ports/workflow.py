from abc import ABC, abstractmethod
from typing import Dict, Any

class WorkflowPort(ABC):
    """
    Workflow Port interface.
    Decouples background workflow engines (Temporal, Prefect, Airflow).
    """
    @abstractmethod
    def start_workflow(self, workflow_name: str, payload: Dict[str, Any]) -> str:
        """Inicia uma instância de workflow em segundo plano e retorna seu ID."""
        pass

    @abstractmethod
    def cancel_workflow(self, workflow_id: str):
        """Cancela ou encerra um workflow ativo."""
        pass

    @abstractmethod
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Consulta o estado atual (running, completed, failed) de um workflow."""
        pass
