from typing import List, Optional
from src.core.cognition.reflection_repository import ReflectionRepository
from src.core.cognition.reflection_service import ReflectionService
from src.core.cognition.models import Reflection, Lesson

class ReflectionAPI:
    """
    Reflection Facade API (Sprint 6.4).
    Isola a consulta e geração de reflexões e lições aprendidas do sistema.
    """
    def __init__(self, repository: ReflectionRepository, service: ReflectionService):
        self.repository = repository
        self.service = service

    def generate(self, experiment_id: str, related_belief_id: int) -> Reflection:
        """Gera uma reflexão pós-experimento e extrai lições estruturadas."""
        return self.service.generate_reflection(experiment_id, related_belief_id)

    def get(self, reflection_id: int) -> Optional[Reflection]:
        """Busca uma reflexão pelo ID."""
        return self.repository.get_reflection(reflection_id)

    def list_by_experiment(self, experiment_id: str) -> List[Reflection]:
        """Lista reflexões associadas a um experimento."""
        return self.repository.get_reflections_by_experiment(experiment_id)

    def get_lessons_for_reflection(self, reflection_id: int) -> List[Lesson]:
        """Busca lições aprendidas vinculadas a uma reflexão."""
        return self.repository.get_lessons_by_reflection(reflection_id)

    def list_all_lessons(self) -> List[Lesson]:
        """Busca todas as lições aprendidas persistidas no sistema."""
        return self.repository.get_lessons()
