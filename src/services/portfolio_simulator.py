from typing import List
from src.revenue_os.analytics.portfolio_state import PortfolioState, PortfolioAsset, PositionStatus
from src.revenue_os.analytics.capital_allocator import CapitalAllocatorEngine

class PortfolioSimulator:
    """
    Simula cenários de mercado e a resposta de mitigação de risco do Lean Quant Fund.
    """
    
    @staticmethod
    def simulate_day_cycle(budget: float, assets: List[PortfolioAsset]) -> PortfolioState:
        # Estado Inicial
        state = PortfolioState(
            total_budget=budget,
            available_capital=budget,
            active_experiments=assets
        )
        
        # O Motor entra em cena
        engine = CapitalAllocatorEngine()
        new_state = engine.rebalance(state)
        
        return new_state
