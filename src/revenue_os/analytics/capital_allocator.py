from src.revenue_os.analytics.portfolio_state import PortfolioState, PositionStatus

class CapitalAllocatorEngine:
    """
    O Coração do Lean Quant Fund.
    Aplica as regras do ADR-007 (70/20/10) e limites de concentração.
    """
    
    def rebalance(self, state: PortfolioState) -> PortfolioState:
        # Recupera todo o dinheiro do mercado (Simulação de Saque/Liquidação Diária)
        total_pool = state.total_budget
        
        # Filtrar o que será mantido e o que morre
        active_assets = []
        for asset in state.active_experiments:
            # Regras de Corte Rápido (Stop-Loss de baixa confiança ou lucro negativo)
            if asset.expected_profit < 0 or asset.confidence < 0.50:
                asset.status = PositionStatus.EXIT
                asset.allocation = 0.0
            else:
                active_assets.append(asset)
                
        # Se não há nada ativo, paramos.
        if not active_assets:
            state.available_capital = total_pool
            return state

        # Ranqueando os ativos pela métrica soberana: Risk Adjusted Return (RAR)
        active_assets.sort(key=lambda a: a.risk_adjusted_return, reverse=True)
        
        # Limite global por ativo
        max_allowed_per_asset = total_pool * state.risk_limits.max_single_experiment
        
        budget_remaining = total_pool
        
        # --- MULTI-ARMED BANDIT (Abordagem de Tranches) ---
        # 1. Exploitation (Campeões ganham muito, limitados ao teto de 30%)
        # Vamos destinar 70% do pote para os top 50% dos ativos.
        exploitation_pool = total_pool * 0.70
        exploitation_candidates = active_assets[:max(1, len(active_assets) // 2)]
        
        for asset in exploitation_candidates:
            if budget_remaining <= 0:
                break
                
            allocation = min(exploitation_pool / len(exploitation_candidates), max_allowed_per_asset)
            
            # Se for incrivelmente lucrativo e tiver espaço para subir, INCREASE. 
            # Senão, HOLD.
            asset.allocation = allocation
            budget_remaining -= allocation
            
            if allocation >= max_allowed_per_asset:
                asset.status = PositionStatus.INCREASE_POSITION
            else:
                asset.status = PositionStatus.HOLD

        # 2. Exploration / High Risk (Os 30% restantes)
        exploration_candidates = active_assets[len(exploitation_candidates):]
        if exploration_candidates and budget_remaining > 0:
            exploration_pool = budget_remaining
            for asset in exploration_candidates:
                if budget_remaining <= 0:
                    break
                    
                # Teses de Risco não ganham INCREASE_POSITION. Ganham INVEST (pequenas injeções).
                allocation = min(exploration_pool / len(exploration_candidates), max_allowed_per_asset * 0.5) # Limite ainda mais rígido
                asset.allocation = allocation
                budget_remaining -= allocation
                
                # Se for de altíssimo risco
                if asset.risk > 0.6:
                    asset.status = PositionStatus.REDUCE # Começa a sacar lucros cedo do High Risk
                else:
                    asset.status = PositionStatus.INVEST
                    
        # Recolhendo o troco
        state.available_capital = budget_remaining
        
        return state
