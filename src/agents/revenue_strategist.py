from typing import Dict, Any, List
from src.mcp.registry import MCPRegistry

class RevenueStrategistAgent:
    """
    Agente Estrategista Econômico (The CEO).
    Não cria vídeos, não faz cálculo estatístico (quem faz é o DecisionEngine).
    Ele consome o laudo (Campaign Results) e profere a ESTRATÉGIA futura para o MutationAgent.
    """
    def __init__(self, llm_provider=None, mcp_registry: MCPRegistry = None):
        self.llm = llm_provider
        self.registry = mcp_registry

    def generate_strategy(self, campaign_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recebe o resultado de uma campanha que acabou de passar pelo Decision Engine.
        Ex: {"campaign": "EXP-009-001", "winner": "Variant C", "decision": "SCALE", "market_segment": "finance"}
        """
        
        winner = campaign_result.get("winner")
        decision = campaign_result.get("decision")
        segment = campaign_result.get("market_segment", "general")
        
        # Em produção, o LLM cruzará isso com a Knowledge Base e o Market Genome.
        # Aqui, criamos um mock estrutural da abstração gerada pelo LLM.
        
        if decision == "SCALE":
            return {
                "recommendation": "EXPAND",
                "reason": f"Hybrid intent pattern has proven positive economics in the {segment} segment.",
                "next_tests": [
                    "Aumentar ticket médio (AOV) sem mexer no criativo",
                    "Clonar a estrutura do hook mas testar novo nicho adjacente"
                ]
            }
            
        if decision == "ITERATE":
            return {
                "recommendation": "PIVOT_CREATIVE",
                "reason": f"Lucrativo, mas sem escala em {segment}. Precisamos aumentar o alcance (Impressions) sacrificando levemente o 'Hard Sell'.",
                "next_tests": [
                    "Manter produto, testar hook de 'Curiosity' mais abrangente."
                ]
            }
            
        if decision == "KILL":
            return {
                "recommendation": "ABANDON_PATTERN",
                "reason": f"A variante falhou no Triple Gate do nicho {segment}. O Trade-Off econômico não fecha a conta.",
                "next_tests": [
                    "Testar um produto diferente",
                    "Reduzir o Custo de Aquisição apostando em outro canal"
                ]
            }
            
        return {
            "recommendation": "WAIT",
            "reason": "Dados insuficientes para firmar estratégia de portfólio."
        }
