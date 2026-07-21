from pydantic import BaseModel, Field
from typing import List, Dict
from enum import Enum

class PositionStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    INVEST = "INVEST"
    HOLD = "HOLD"
    INCREASE_POSITION = "INCREASE_POSITION"
    REDUCE = "REDUCE"
    EXIT = "EXIT"

class PortfolioAsset(BaseModel):
    experiment_id: str
    allocation: float = Field(0.0)
    expected_profit: float = Field(0.0)
    confidence: float = Field(0.0)
    risk: float = Field(0.0, description="Nível de risco (volatilidade e concentração de mercado)")
    status: PositionStatus = Field(PositionStatus.INVEST)
    
    @property
    def risk_adjusted_return(self) -> float:
        """RAR = Expected Return / Risk"""
        # Se o risco for virtualmente 0, protegemos contra div/0 e inflação irreal
        safe_risk = max(0.05, self.risk)
        return self.expected_profit / safe_risk

class RiskLimits(BaseModel):
    max_single_experiment: float = Field(0.30, description="Nenhum experimento passa de 30% do bolo.")
    max_channel_exposure: float = Field(0.50)

class PortfolioState(BaseModel):
    total_budget: float = Field(...)
    available_capital: float = Field(...)
    active_experiments: List[PortfolioAsset] = Field(default_factory=list)
    risk_limits: RiskLimits = Field(default_factory=RiskLimits)

    def total_allocated(self) -> float:
        return sum(exp.allocation for exp in self.active_experiments)
