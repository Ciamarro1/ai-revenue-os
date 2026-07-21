from typing import List, Optional, Callable, Dict, Any
from src.core.cognition.skill_repository import SkillRepository
from src.core.cognition.skill_service import SkillRegistryService
from src.core.cognition.models import Skill, SkillStep, SkillExecution, SkillStepExecution

class SkillAPI:
    """
    SkillAPI Facade (Sprint 7.2).
    Fachada de fronteira isolando a criação, descoberta e orquestração de Skills cognitivas.
    """
    def __init__(self, repository: SkillRepository, service: SkillRegistryService):
        self.repository = repository
        self.service = service

    def register(self, skill: Skill) -> Skill:
        """Registra uma Skill declarativa na base cognitiva."""
        return self.service.register_skill(skill)

    def discover(self, objective: str) -> List[Skill]:
        """Descobre as Skills recomendadas para um objetivo específico."""
        return self.service.discover_skills(objective)

    def execute(self, skill_name: str, input_data: Dict[str, Any], action_id: Optional[int] = None) -> Dict[str, Any]:
        """Executa sequencialmente os passos de uma Skill, monitorando telemetrias de ferramentas."""
        return self.service.execute_skill(skill_name, input_data, action_id)

    def register_handler(self, cap_name: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """Mapeia um callback funcional para processar uma capacidade exigida."""
        self.service.register_capability_handler(cap_name, handler)

    def get_execution(self, exec_id: int) -> Optional[SkillExecution]:
        """Busca o log detalhado de execução global da Skill."""
        return self.repository.get_skill_execution(exec_id)

    def get_step_executions(self, skill_exec_id: int) -> List[SkillStepExecution]:
        """Busca o histórico de execuções de cada etapa (Step) pertencente a uma SkillExecution."""
        return self.repository.get_skill_step_executions(skill_exec_id)
