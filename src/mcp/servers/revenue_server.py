from src.mcp.registry import MCPServer
from src.revenue_os.analytics.attribution import AttributionEngine

class RevenueServer(MCPServer):
    def __init__(self):
        super().__init__("RevenueServer")
        self.register_tool(
            "calculate_profit",
            "Busca vendas confirmadas e subtrai o custo de geração.",
            self.calculate_profit
        )
        self.register_tool(
            "calculate_roas",
            "Calcula Retorno sobre Investimento Publicitário ou Geração.",
            self.calculate_roas
        )
        self.register_tool(
            "distribute_attribution",
            "Aplica o modelo 40/40/20 de crédito sobre o funil de interações.",
            self.distribute_attribution
        )
        
        self.attribution_engine = AttributionEngine()

    def calculate_profit(self, experiment_id: str):
        pass

    def calculate_roas(self, experiment_id: str):
        pass
        
    def distribute_attribution(self, touchpoints: list, total_revenue: float):
        return self.attribution_engine.distribute_revenue(touchpoints, total_revenue)
