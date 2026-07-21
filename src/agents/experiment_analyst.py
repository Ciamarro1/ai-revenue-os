import json
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
import os
from pydantic_ai.models.test import TestModel

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "dummy_key_for_import"

from src.mcp.registry import MCPRegistry

logger = logging.getLogger("agents.experiment_analyst")

# ==========================================
# Schemas de Entrada e Saída
# ==========================================
class MetricsInput(BaseModel):
    hypothesis: str
    winner: Optional[str]
    is_significant: bool
    trade_off_detected: bool
    sample_size_total: int
    confidence: float
    effect_size: float

class AnalysisConclusion(BaseModel):
    conclusion: str = Field(description="A conclusão narrativa do experimento baseada nas métricas.")
    is_valid: bool = Field(description="O experimento gerou uma resposta matematicamente válida?")
    action_items: List[str] = Field(description="O que deve ser feito a seguir (ex: 'Escalar', 'Descartar', 'Mais dados').")
    effect_category: str = Field(description="'Massivo', 'Moderado', 'Leve' ou 'Nenhum'.")

# ==========================================
# Inicialização do Agente PydanticAI
# ==========================================
agent = Agent(
    'google:gemini-1.5-flash',
    deps_type=MetricsInput,
    output_type=AnalysisConclusion,
    system_prompt=(
        "Você é um Analista de Experimentos Científicos em um fundo quantitativo de atenção."
        "Você analisa os resultados de um teste A/B para uma hipótese criativa."
        "Regras estritas:"
        "1. Se sample_size_total < 30, conclua que as evidências são insuficientes."
        "2. Se trade_off_detected for True, sugira investigar o trade-off."
        "3. Se is_significant for False, declare empate matemático."
        "4. Se houver um vencedor com significância, classifique o effect_size e recomende escala."
    )
)

class ExperimentAnalystAgent:
    """
    Agente Cientista (Analista).
    O domínio matemático é avaliado rigidamente no Core Python (sem IA).
    PydanticAI é usado opcionalmente como Interface de enriquecimento cognitivo.
    """
    def __init__(self, llm_provider=None, mcp_registry: MCPRegistry = None, use_test_model: bool = True):
        self.llm = llm_provider
        self.registry = mcp_registry
        self.model = TestModel() if use_test_model else None

    def analyze_results(self, metrics_report: Dict[str, Any]) -> str:
        if "error" in metrics_report:
            return f"Erro na análise: {metrics_report['error']}"
            
        hypothesis = metrics_report.get("hypothesis", "")
        winner = metrics_report.get("winner")
        sig = metrics_report.get("is_significant", False)
        trade = metrics_report.get("trade_off_detected", False)
        n = metrics_report.get("sample_size_total", 0)
        
        # --- DOMÍNIO DETERMINÍSTICO CORE (Regra Inviolável #1) ---
        if n < 30:
            conclusion_text = f"Insufficient evidence. Amostra muito pequena ({n}). Precisamos de mais dados."
        elif trade:
            conclusion_text = f"Trade-off detected. A variante {winner} venceu na métrica principal, mas destruiu a métrica secundária. Need more experiments para isolar a causa."
        elif not sig:
            conclusion_text = f"No statistically significant winner. Nenhuma das variantes provou superioridade matemática (Confiança: {metrics_report.get('confidence', 0.0)*100}%)."
        elif winner:
            eff = metrics_report.get('effect_size', 0.0)
            impact = "Massivo" if eff > 0.8 else "Moderado" if eff > 0.5 else "Leve"
            conclusion_text = f"{winner} validated. A variante {winner} é a vencedora absoluta com {metrics_report.get('confidence', 0.0)*100}% de confiança. O tamanho do efeito é {impact} (d={eff}). Sugestão: Escalar as características de {winner}."
        else:
            conclusion_text = "Conclusão inconclusiva."

        # --- INTERFACE DE ENRIQUECIMENTO VIA PYDANTICAI ---
        # Apenas executa se não for o modelo de teste e se houver chaves de IA.
        if not self.model:
            try:
                input_data = MetricsInput(
                    hypothesis=hypothesis,
                    winner=winner,
                    is_significant=sig,
                    trade_off_detected=trade,
                    sample_size_total=n,
                    confidence=metrics_report.get("confidence", 0.0),
                    effect_size=metrics_report.get("effect_size", 0.0)
                )
                prompt = f"Gere uma conclusão narrativa enriquecida para as seguintes métricas:\n{input_data.model_dump_json(indent=2)}"
                result = agent.run_sync(prompt, deps=input_data)
                conclusion: AnalysisConclusion = result.output
                print(f"💡 [ExperimentAnalyst | PydanticAI Enriquecimento]: {conclusion.conclusion}")
            except Exception as e:
                logger.warning(f"Falha ao chamar PydanticAI para enriquecimento: {e}")
                
        return f"[{hypothesis}] {conclusion_text}"
