from typing import Dict, Any

class Scoreboard:
    """
    O placar que julga se o AI Revenue OS supera um humano inexperiente.
    Calcula o lucro hipotético do nosso Capital Allocator vs Baselines ingênuas.
    """
    def __init__(self):
        self.metrics = {
            "ai_revenue_os_profit": 0.0,
            "baseline_equal_profit": 0.0,
            "baseline_max_ctr_profit": 0.0,
            "cycles_run": 0,
            "cycles_since_last_discovery": 0,
            "discovery_velocity_avg": 0.0,
            "patterns_discovered": 0
        }
        
    def register_pattern_discovery(self):
        """Chamado quando um experimento entra na Genome Library."""
        self.metrics["patterns_discovered"] += 1
        
        # Média Móvel de Velocidade (Ex: Descobriu o padrão em 14 ciclos)
        current_avg = self.metrics["discovery_velocity_avg"]
        total_p = self.metrics["patterns_discovered"]
        cycles_spent = self.metrics["cycles_since_last_discovery"]
        
        if total_p == 1:
            self.metrics["discovery_velocity_avg"] = cycles_spent
        else:
            self.metrics["discovery_velocity_avg"] = ((current_avg * (total_p - 1)) + cycles_spent) / total_p
            
        self.metrics["cycles_since_last_discovery"] = 0 # Reseta o timer
        
    def evaluate_cycle(self, total_budget: float, ai_allocations: Dict[str, float], actual_profits_per_variant: Dict[str, float], ctr_per_variant: Dict[str, float]):
        """
        No final de um ciclo Shadow Mode, nós alimentamos os lucros reais que CADA variante
        produziu (em ROI). O Scoreboard calcula o $ ganho por cada estratégia.
        """
        self.metrics["cycles_run"] += 1
        self.metrics["cycles_since_last_discovery"] += 1
        
        # 1. AI Revenue OS Performance
        ai_profit = sum(ai_allocations[var] * actual_profits_per_variant[var] for var in ai_allocations if var in actual_profits_per_variant)
        self.metrics["ai_revenue_os_profit"] += ai_profit
        
        # 2. Baseline: Equal Allocation (Divide tudo igual)
        variants = list(actual_profits_per_variant.keys())
        if variants:
            equal_budget = total_budget / len(variants)
            equal_profit = sum(equal_budget * actual_profits_per_variant[var] for var in variants)
            self.metrics["baseline_equal_profit"] += equal_profit
        
        # 3. Baseline: Max CTR (Joga tudo em quem teve maior CTR ontem)
        if ctr_per_variant:
            best_ctr_variant = max(ctr_per_variant, key=ctr_per_variant.get)
            if best_ctr_variant in actual_profits_per_variant:
                max_ctr_profit = total_budget * actual_profits_per_variant[best_ctr_variant]
                self.metrics["baseline_max_ctr_profit"] += max_ctr_profit

    def get_summary(self) -> Dict[str, Any]:
        ai_won = self.metrics["ai_revenue_os_profit"] > self.metrics["baseline_equal_profit"]
        return {
            "Cycles": self.metrics["cycles_run"],
            "AI_OS_Profit": round(self.metrics["ai_revenue_os_profit"], 2),
            "Equal_Baseline_Profit": round(self.metrics["baseline_equal_profit"], 2),
            "MaxCTR_Baseline_Profit": round(self.metrics["baseline_max_ctr_profit"], 2),
            "Discovery_Velocity_Cycles": round(self.metrics["discovery_velocity_avg"], 1),
            "Patterns_Cataloged": self.metrics["patterns_discovered"],
            "Status": "READY_FOR_SOFT_LAUNCH" if ai_won and self.metrics["cycles_run"] >= 100 else "NEEDS_MORE_SHADOW_CYCLES"
        }
