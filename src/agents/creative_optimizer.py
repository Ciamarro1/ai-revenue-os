import json
import os
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "dummy_key_for_import"


# ==========================================
# Schemas de Entrada e Saída
# ==========================================
class OptimizerInput(BaseModel):
    brief_title: str
    original_hook: str
    findings: List[Dict[str, Any]] = Field(description="Falhas reportadas pelo Critic")

class OptimizedCreative(BaseModel):
    hook: str = Field(description="O novo hook otimizado para corrigir as falhas.")
    search_terms: List[str] = Field(description="Novos termos de busca para visual mais dinâmico, se necessário.")
    reasoning: str = Field(description="Explicação passo-a-passo de por que essa mudança vai aumentar a retenção.")

# ==========================================
# Inicialização do Agente PydanticAI
# ==========================================
agent = Agent(
    'google:gemini-1.5-flash',
    deps_type=OptimizerInput,
    output_type=OptimizedCreative,
    system_prompt=(
        "Você é um Creative Optimizer (Engenheiro de UX e Retenção) de um laboratório AI Revenue OS. "
        "Seu objetivo é analisar um 'Brief', o 'Hook original' que falhou e as 'Falhas' reportadas pelo crítico. "
        "Você deve gerar um NOVO hook e NOVOS search_terms que resolvam EXATAMENTE as falhas apontadas, "
        "focando em aumentar a retenção e o dinamismo visual. Seja direto e pragmático."
    )
)

class CreativeOptimizerAgent:
    """
    Agente responsável por otimizar campanhas reprovadas (EXP-006).
    Migrado para PydanticAI para garantir type-safety e estruturação do Output.
    """
    
    def __init__(self, max_attempts: int = 3, use_test_model: bool = True):
        self.max_attempts = max_attempts
        self.current_attempt = 1
        # TestModel não consome API, ele gera dados estáticos válidos pelo Schema. Ótimo para Shadow Mode.
        self.model = TestModel() if use_test_model else None

    def optimize(
        self,
        brief: Dict[str, Any],
        copy_data: Dict[str, Any],
        render_report: Dict[str, Any],
        critic_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera uma nova 'Copy' otimizada para corrigir as falhas reportadas.
        """
        print(f"🧠 [CreativeOptimizer-PydanticAI] Iniciando Attempt {self.current_attempt}/{self.max_attempts}...")
        
        if self.current_attempt > self.max_attempts:
            raise RecursionError(f"Limite máximo de otimizações atingido ({self.max_attempts}). Acionando HUMAN REVIEW.")

        findings = critic_report.get("findings", [])
        
        input_data = OptimizerInput(
            brief_title=brief.get("title", "Desconhecido"),
            original_hook=copy_data.get("hook", ""),
            findings=findings
        )
        
        print("💡 [CreativeOptimizer] Invocando LLM via PydanticAI (TestModel=" + str(self.model is not None) + ")")
        
        # Executa o agente PydanticAI
        prompt = (
            f"Otimize esta cópia com base nas falhas encontradas.\n"
            f"Brief: {input_data.brief_title}\n"
            f"Hook Original: {input_data.original_hook}\n"
            f"Falhas:\n{json.dumps(input_data.findings, indent=2)}"
        )
        
        if self.model:
            result = agent.run_sync(prompt, deps=input_data, model=self.model)
        else:
            result = agent.run_sync(prompt, deps=input_data)
            
        optimized: OptimizedCreative = result.output
        
        print(f"  => LLM Reasoning: {optimized.reasoning}")
        print(f"  => Novo Hook gerado: {optimized.hook}")
        
        new_copy = dict(copy_data)
        new_copy["hook"] = optimized.hook
        if optimized.search_terms:
            new_copy["search_terms"] = optimized.search_terms
            
        self.current_attempt += 1
        
        print("✅ [CreativeOptimizer] Nova Copy gerada estruturada e tipada!")
        return new_copy
