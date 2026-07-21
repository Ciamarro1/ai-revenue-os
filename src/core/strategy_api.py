from typing import List, Optional
from src.core.cognition.strategy_repository import StrategyRepository
from src.core.cognition.strategy_service import StrategyService
from src.core.cognition.models import Goal, Strategy, Constraint, Opportunity

class StrategyAPI:
    """
    Strategy Facade API (Sprint 6.6).
    Isola formulação de metas de longo prazo, estratégias e otimização multi-objetivo.
    """
    def __init__(self, repository: StrategyRepository, service: StrategyService):
        self.repository = repository
        self.service = service

    def create_goal(self, name: str, target_metric: str, target_value: float, current_value: float = 0.0) -> Goal:
        """Cadastra um novo objetivo de longo prazo (Goal)."""
        goal = Goal(name=name, target_metric=target_metric, target_value=target_value, current_value=current_value, status="Active")
        return self.repository.save_goal(goal)

    def create_strategy(
        self,
        goal_id: int,
        statement: str,
        expected_revenue: float = 0.0,
        expected_learning: float = 0.0,
        risk: float = 1.0,
        cost: float = 1.0
    ) -> Strategy:
        """Cadastra uma estratégia candidata vinculada a um Goal."""
        strategy = Strategy(
            goal_id=goal_id,
            statement=statement,
            expected_revenue=expected_revenue,
            expected_learning=expected_learning,
            risk=risk,
            cost=cost,
            status="Proposed"
        )
        return self.repository.save_strategy(strategy)

    def optimize(self, goal_id: int) -> List[Strategy]:
        """Calcula a utilidade composta multi-objetivo e ativa/prioriza as estratégias."""
        return self.service.optimize_strategies(goal_id)

    def create_constraint(self, description: str, constraint_type: str, value: float) -> Constraint:
        """Adiciona uma restrição física/financeira do sistema."""
        constraint = Constraint(description=description, constraint_type=constraint_type, value=value)
        return self.repository.save_constraint(constraint)

    def create_opportunity(
        self,
        name: str,
        description: str,
        expected_revenue: float = 0.0,
        expected_learning: float = 0.0
    ) -> Opportunity:
        """Registra um nicho de oportunidade mapeado no mercado."""
        # Score inicial composto simples para oportunidades
        score = expected_revenue + (expected_learning * 10.0)
        opp = Opportunity(
            name=name,
            description=description,
            expected_revenue=expected_revenue,
            expected_learning=expected_learning,
            score=score
        )
        return self.repository.save_opportunity(opp)

    def get_goals(self) -> List[Goal]:
        """Lista todos os goals cadastrados."""
        return self.repository.get_goals()

    def get_strategies(self) -> List[Strategy]:
        """Lista todas as estratégias registradas."""
        return self.repository.get_strategies()

    def get_constraints(self) -> List[Constraint]:
        """Lista todas as restrições vigentes."""
        return self.repository.get_constraints()

    def get_opportunities(self) -> List[Opportunity]:
        """Lista as oportunidades de mercado ordenadas por atratividade."""
        return self.repository.get_opportunities()
