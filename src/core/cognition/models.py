from datetime import datetime, timezone
from typing import Optional, Dict, Any, Union, List
from pydantic import BaseModel, Field

class Belief(BaseModel):
    id: Optional[int] = None
    statement: str = Field(..., description="Crença sobre o comportamento de tráfego/monetização")
    confidence_score: float = Field(0.50, ge=0.0, le=1.0, description="Nível de confiança (0.0 a 1.0)")
    updated_at: Optional[str] = None

class Evidence(BaseModel):
    id: Optional[int] = None
    hypothesis_id: Optional[int] = None
    experiment_id: str = Field(..., description="ID do experimento que originou a evidência")
    claim: str = Field(..., description="Afirmação/fato observado")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Nível de significância estatística ou confiança")
    impact: str = Field(..., description="Impacto: Positivo, Negativo ou Neutro")
    timestamp: Optional[str] = None
    narrative: Optional[str] = Field(None, description="Enriquecimento narrativo descritivo gerado pelo agente")

class Learning(BaseModel):
    id: Optional[int] = None
    experiment_id: str = Field(..., description="ID do experimento associado")
    pattern: str = Field(..., description="Padrão ou falha recorrente identificada")
    severity: str = Field(..., description="Nível de severidade (HIGH, MEDIUM, LOW)")
    description: str = Field(..., description="Descrição detalhada do aprendizado")
    created_at: Optional[str] = None

class Observation(BaseModel):
    id: Optional[int] = None
    source: str = Field(..., description="Origem da observação (ex: pinterest_scraper)")
    metric_name: str = Field(..., description="Nome da métrica observada (ex: CTR, Clicks)")
    value: float = Field(..., description="Valor da métrica")
    timestamp: Optional[str] = None
    raw_data: Optional[str] = Field(None, description="Dados brutos adicionais em formato texto ou JSON")

class GraphNode(BaseModel):
    id: str = Field(..., description="ID único do nó (ex: 'observation:1')")
    type: str = Field(..., description="Tipo do nó (observation, evidence, belief, decision, experiment)")
    label: str = Field(..., description="Rótulo legível para visualização")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais do nó")

class GraphEdge(BaseModel):
    source: str = Field(..., description="ID do nó de origem")
    target: str = Field(..., description="ID do nó de destino")
    relation_type: str = Field(..., description="Tipo da relação (originates, supports, modifies, triggers)")
    weight: float = Field(1.0, description="Peso ou força da relação")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais da aresta")

class Hypothesis(BaseModel):
    id: Optional[int] = None
    statement: str = Field(..., description="Afirmação causal / hipótese científica")
    confidence_score: float = Field(0.50, ge=0.0, le=1.0, description="Escore de confiança (0.0 a 1.0)")
    status: str = Field("Proposed", description="Status da hipótese: Proposed, Validated, Rejected")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Reflection(BaseModel):
    id: Optional[int] = None
    experiment_id: str = Field(..., description="ID do experimento associado")
    analysis: str = Field(..., description="Análise descritiva da reflexão")
    probable_cause: str = Field(..., description="Causa provável identificada para o resultado")
    confidence_delta: float = Field(..., description="Diferença de confiança observada no loop")
    bayesian_explanation: Dict[str, Any] = Field(default_factory=dict, description="Explicação Bayesiana detalhada (prior, posterior, likelihood)")
    timestamp: Optional[str] = None

class Lesson(BaseModel):
    id: Optional[int] = None
    reflection_id: Optional[int] = None
    pattern_detected: str = Field(..., description="Padrão detectado (sucesso ou falha recorrente)")
    actionable_insight: str = Field(..., description="Insight acionável ou instrução futura")
    severity: str = Field("medium", description="Severidade ou relevância (high, medium, low)")
    created_at: Optional[str] = None

class Objective(BaseModel):
    id: Optional[int] = None
    description: str = Field(..., description="Descrição detalhada do objetivo de negócio")
    target_metric: str = Field(..., description="Métrica chave alvo (ex: CTR, ROI)")
    status: str = Field("Active", description="Status do objetivo: Active, Achieved, Abandoned")
    created_at: Optional[str] = None

class Plan(BaseModel):
    id: Optional[int] = None
    objective_id: int = Field(..., description="ID do objetivo associado")
    statement: str = Field(..., description="Diretriz estratégica ou enunciado do plano")
    status: str = Field("Draft", description="Status: Draft, Approved, Executing, Completed")
    priority_score: float = Field(1.0, description="Escore composto de priorização do plano")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class PlanStep(BaseModel):
    id: Optional[int] = None
    plan_id: int = Field(..., description="ID do plano pai")
    step_number: int = Field(..., description="Ordem de execução do passo")
    action_description: str = Field(..., description="Descrição detalhada da ação táctica")
    experiment_id: Optional[str] = Field(None, description="ID do experimento associado se gerado")
    status: str = Field("Pending", description="Status do passo: Pending, Enqueued, Executing, Completed, Failed")
    created_at: Optional[str] = None

class Goal(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., description="Nome do objetivo de longo prazo")
    target_metric: str = Field(..., description="Métrica alvo")
    target_value: float = Field(..., description="Valor alvo a ser atingido")
    current_value: float = Field(0.0, description="Valor atual da métrica")
    status: str = Field("Active", description="Status do Goal: Active, Completed, Paused")
    created_at: Optional[str] = None

class Strategy(BaseModel):
    id: Optional[int] = None
    goal_id: int = Field(..., description="ID do Goal associado")
    statement: str = Field(..., description="Enunciado estratégico")
    expected_revenue: float = Field(0.0, description="Retorno de receita esperado")
    expected_learning: float = Field(0.0, description="Retorno de aprendizado esperado")
    risk: float = Field(1.0, description="Grau de risco da estratégia")
    cost: float = Field(1.0, description="Custo financeiro ou operacional")
    status: str = Field("Proposed", description="Status: Proposed, Active, Completed")
    priority_score: float = Field(1.0, description="Score composto multi-objetivo")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Constraint(BaseModel):
    id: Optional[int] = None
    description: str = Field(..., description="Descrição do limitador operacional")
    constraint_type: str = Field(..., description="Tipo de restrição: Budget, RateLimit, TimeLimit")
    value: float = Field(..., description="Valor limite")
    created_at: Optional[str] = None

class Opportunity(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., description="Nome do nicho ou oportunidade de mercado")
    description: str = Field(..., description="Descrição detalhada da oportunidade")
    expected_revenue: float = Field(0.0, description="Receita esperada da oportunidade")
    expected_learning: float = Field(0.0, description="Aprendizado esperado da oportunidade")
    score: float = Field(1.0, description="Escore de atratividade da oportunidade")
    created_at: Optional[str] = None

class Action(BaseModel):
    id: Optional[int] = None
    step_id: int = Field(..., description="ID do passo do plano associado")
    name: str = Field(..., description="Nome descritivo da ação executável")
    status: str = Field("Pending", description="Status: Pending, Executing, Completed, Failed, Cancelled, Paused")
    retry_count: int = Field(0, description="Contagem atual de tentativas de reexecução")
    max_retries: int = Field(3, description="Número máximo de tentativas permitidas")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ActionDependency(BaseModel):
    id: Optional[int] = None
    action_id: int = Field(..., description="ID da ação dependente")
    depends_on_action_id: int = Field(..., description="ID da ação pré-requisito")

class ExecutionHistory(BaseModel):
    id: Optional[int] = None
    action_id: int = Field(..., description="ID da ação executada")
    status: str = Field(..., description="Status final ou intermediário registrado")
    error_message: Optional[str] = Field(None, description="Mensagem de erro em caso de falha")
    executed_at: Optional[str] = None

class Provider(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., description="Nome do provedor externo (ex: Replicate, Pinterest OAuth)")
    description: str = Field(..., description="Descrição operacional do provedor")
    status: str = Field("Active", description="Status do provedor: Active, Inactive")
    created_at: Optional[str] = None

class Tool(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., description="Nome da ferramenta (ex: Pinterest API, Flux)")
    version: str = Field("1.0.0", description="Versão da ferramenta")
    provider_id: int = Field(..., description="ID do provedor associado")
    capabilities: str = Field(..., description="Lista de capacidades suportadas separadas por vírgula")
    cost: float = Field(0.0, description="Custo unitário estimado por execução")
    latency: float = Field(0.0, description="Latência média histórica em segundos")
    reliability: float = Field(1.0, description="Taxa de sucesso histórica (0.0 a 1.0)")
    health_score: float = Field(1.0, description="Status de saúde atual")
    created_at: Optional[str] = None

class Capability(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., description="Nome descritivo da capacidade única (ex: 'Generate Image')")
    description: str = Field(..., description="Descrição detalhada do propósito")
    created_at: Optional[str] = None

class ToolExecution(BaseModel):
    id: Optional[int] = None
    tool_id: int = Field(..., description="ID da ferramenta executada")
    latency: float = Field(..., description="Tempo de execução medido em segundos")
    cost: float = Field(..., description="Custo real computado")
    success: bool = Field(..., description="Resultado de sucesso ou falha da execução")
    error_message: Optional[str] = Field(None, description="Erro logado se houver")
    executed_at: Optional[str] = None

class SkillStep(BaseModel):
    id: Optional[int] = None
    skill_id: Optional[int] = None
    step_order: int = Field(..., description="Ordem sequencial da etapa")
    capability_required: str = Field(..., description="Capacidade exigida nesta etapa")
    tool_required: Optional[str] = Field(None, description="Nome da ferramenta específica se exigida")
    input_mapping: str = Field("{}", description="Mapeamento de inputs da etapa em JSON")
    output_mapping: str = Field("{}", description="Mapeamento de outputs da etapa em JSON")
    retry_policy: str = Field("{}", description="Regras de retentativa em JSON")

class Skill(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., description="Nome único da habilidade de negócio")
    description: str = Field(..., description="Descrição detalhada do propósito")
    objective: str = Field(..., description="Objetivo ou tipo de meta associado")
    input_schema: str = Field("{}", description="Campos esperados na entrada em JSON")
    output_schema: str = Field("{}", description="Campos retornados na saída em JSON")
    constraints: str = Field("{}", description="Restrições da habilidade em JSON")
    metadata: str = Field("{}", description="Metadados adicionais em JSON")
    created_at: Optional[str] = None
    steps: List[SkillStep] = Field(default_factory=list, description="Lista ordenada de passos")

class SkillExecution(BaseModel):
    id: Optional[int] = None
    skill_id: int = Field(..., description="ID da Skill executada")
    status: str = Field("Pending", description="Status da execução: Pending, Running, Completed, Failed")
    input_data: str = Field("{}", description="Valores de entrada utilizados em JSON")
    output_data: str = Field("{}", description="Valores de saída produzidos em JSON")
    error_message: Optional[str] = Field(None, description="Erro logado se houver")
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class SkillStepExecution(BaseModel):
    id: Optional[int] = None
    skill_execution_id: int = Field(..., description="ID da execução da Skill")
    step_id: int = Field(..., description="ID do passo executado")
    status: str = Field("Pending", description="Status: Pending, Running, Completed, Failed")
    tool_execution_id: Optional[int] = Field(None, description="ID da execução de ferramenta correspondente")
    latency: float = Field(0.0, description="Tempo decorrido na etapa")
    error_message: Optional[str] = Field(None, description="Mensagem de erro se falhar")
    executed_at: Optional[str] = None
