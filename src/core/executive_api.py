from typing import List, Optional, Callable, Any
from src.core.cognition.executive_repository import ExecutiveRepository
from src.core.cognition.executive_service import ExecutiveService
from src.core.cognition.models import Action, ExecutionHistory

class ExecutiveAPI:
    """
    Executive Facade API (Sprint 7.0).
    Fachada que expõe comandos de execução táctica, monitoramento e gerenciamento de estados.
    """
    def __init__(self, repository: ExecutiveRepository, service: ExecutiveService):
        self.repository = repository
        self.service = service

    def create_action(self, step_id: int) -> Action:
        """Converte um passo de plano estratégico em ação executável."""
        return self.service.create_action_from_step(step_id)

    def add_dependency(self, action_id: int, depends_on_action_id: int) -> None:
        """Adiciona uma restrição de dependência entre duas ações."""
        self.repository.add_dependency(action_id, depends_on_action_id)

    def execute(self, action_id: int, execution_callback: Optional[Callable[[], Any]] = None) -> bool:
        """Executa a ação disparando o callback de lógica e gerenciando retries/dependências."""
        return self.service.execute_action(action_id, execution_callback)

    def pause(self, action_id: int) -> None:
        """Pausa uma execução ativa de ação."""
        self.service.pause_action(action_id)

    def cancel(self, action_id: int) -> None:
        """Cancela permanentemente uma execução de ação."""
        self.service.cancel_action(action_id)

    def get_action(self, action_id: int) -> Optional[Action]:
        """Busca uma ação pelo ID."""
        return self.repository.get_action(action_id)

    def get_actions(self) -> List[Action]:
        """Lista todas as ações ativas e históricas."""
        return self.repository.get_actions()

    def get_execution_history(self, action_id: int) -> List[ExecutionHistory]:
        """Busca todo o histórico de execuções e retentativas de uma ação."""
        return self.repository.get_execution_history(action_id)
