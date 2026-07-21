from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum

class ReleaseChannel(Enum):
    LAB = "LAB"
    SHADOW = "SHADOW"
    CANARY = "CANARY"
    LIMITED = "LIMITED"
    PRODUCTION = "PRODUCTION"
    
    @classmethod
    def can_promote(cls, current: 'ReleaseChannel', target: 'ReleaseChannel', force: bool = False) -> bool:
        if force: return True
        order = list(cls)
        try:
            curr_idx = order.index(current)
            tgt_idx = order.index(target)
            return tgt_idx == curr_idx + 1
        except ValueError:
            return False

class Decision(Enum):
    SCALE = "SCALE"
    ITERATE = "ITERATE"
    COLLECT_MORE_DATA = "COLLECT_MORE_DATA"
    KILL = "KILL"

class Hypothesis(BaseModel):
    statement: str = Field(..., description="Afirmação causal que o experimento tenta provar.")
    metric_target: str = Field(..., description="A métrica principal que deve ser afetada.")

class Variant(BaseModel):
    id: str = Field(..., description="Identificador da variante (A, B, C...)")
    description: str = Field(..., description="Descrição detalhada do que muda nesta variante.")

class Economics(BaseModel):
    generation_cost_usd: float = Field(0.0, description="Custo somado de APIs (TTS, LLMs, etc).")
    revenue_usd: float = Field(0.0, description="Lucro atribuível ao experimento.")
    utm_url: Optional[str] = Field(None, description="Dynamic tracked affiliate redirect link")
    epc: float = Field(0.0, description="Earnings Per Click")
    rpc: float = Field(0.0, description="Revenue Per Click")
    roi: float = Field(0.0, description="Return on Investment")
    ltv: float = Field(0.0, description="Estimated Lifetime Value")
    cpa: float = Field(0.0, description="Cost Per Acquisition")

class RealWorldMetrics(BaseModel):
    impressions: int = Field(0)
    traffic_sources: List[str] = Field(default_factory=lambda: ["youtube"])
    volatility_index: float = Field(0.0, description="0 a 1.0 (onde 1.0 é extremamente instável e pontual).")
    ctr_percent: float = Field(0.0)
    retention_3s_percent: float = Field(0.0)
    completion_rate_percent: float = Field(0.0)
    landing_visit_percent: float = Field(0.0, description="Visitantes que de fato chegaram e carregaram a landing page.")
    conversion_count: int = Field(0)
    aov_usd: float = Field(0.0, description="Average Order Value")
    profit_usd: float = Field(0.0, description="Lucro final após custos de mídia/geração.")

class ContentGenome(BaseModel):
    emotion: str = Field(...)
    format: str = Field(...)
    curiosity_level: Optional[str] = Field("medium", description="curiosity factor level")
    urgency_level: Optional[str] = Field("medium", description="urgency factor level")
    visual_style: Optional[str] = Field("clean", description="visual design theme")
    color_palette: Optional[str] = Field("vibrant", description="dominant colors theme")
    hook_type: Optional[str] = Field("question", description="hook opening style")
    difficulty: Optional[str] = Field("beginner", description="target skill/difficulty level")
    offer_type: Optional[str] = Field("affiliate", description="offer type")
    pain_point: Optional[str] = Field("time", description="customer pain point")
    benefit: Optional[str] = Field("money", description="value proposition benefit")
    seasonality: Optional[str] = Field("evergreen", description="seasonal timing context")

class MarketGenome(BaseModel):
    audience: str = Field(...)
    intent: str = Field(...)
    price_point: str = Field(...)

class EconomicGenome(BaseModel):
    cpa: float = Field(...)
    conversion_rate: float = Field(...)
    margin: float = Field(...)

class RevenueGenome(BaseModel):
    genome_id: str
    content_genome: ContentGenome
    market_genome: MarketGenome
    economic_genome: EconomicGenome

class ExperimentContract(BaseModel):
    experiment_id: str
    run_id: Optional[str] = Field(None, description="ID da execução (Run Ledger) que originou este experimento.")
    baseline_id: Optional[str] = Field(None, description="ID do experimento base para cálculo relativo de evolução.")
    market_segment: str = Field("general", description="Nicho específico do experimento.")
    scalability_score: float = Field(0.0, description="Potencial projetado de escala do conteúdo.")
    hypothesis: Hypothesis
    variant: Variant
    genome: Optional[RevenueGenome] = None
    economics: Economics
    creative_hash: str
    published_at: Optional[str] = None
    platform: str = "youtube"
    
    real_world_metrics: RealWorldMetrics = Field(default_factory=RealWorldMetrics)
    reward_score: float = Field(0.0)
    confidence_score: float = Field(0.0, description="Nível de significância estatística do teste (ex: 0.95 = 95%).")
    sample_size: int = Field(0, description="Volume total da amostra de impressões.")
    status: str = Field("AWAITING_DATA")
    learning_value_score: float = Field(0.0, description="Métrica de ganho de conhecimento obtido no ciclo.")

    def calculate_reward(self) -> float:
        """
        Nova Função de Recompensa Econômica (EXP-009):
        Revenue Score = 0.30 ProfitScore + 0.20 ConversionRate + 0.20 CTR + 0.15 Retention + 0.10 Stability + 0.05 Novelty
        """
        m = self.real_world_metrics
        # Normalizando profit para score (simplificação, 1.0 = ótimo lucro)
        profit_score = min(1.0, max(0.0, m.profit_usd / 1000.0))
        # Normalizando conversão baseada em visitas
        visitors = m.impressions * (m.ctr_percent/100) * (m.landing_visit_percent/100)
        conv_rate = (m.conversion_count / visitors) * 100 if visitors > 0 else 0.0
        conv_score = min(1.0, conv_rate / 10.0)
        
        # CTR score: CTR percent normalized to 0-1.0
        ctr_score = min(1.0, m.ctr_percent / 10.0)
        # Retention score: retention_3s_percent normalized to 0-1.0
        retention_score = min(1.0, m.retention_3s_percent / 100.0)
        # Stability score: 1.0 - volatility_index
        stability = 1.0 - m.volatility_index
        # Novelty: default to 1.0
        novelty = 1.0
        
        raw_score = (
            (0.30 * profit_score) +
            (0.20 * conv_score) +
            (0.20 * ctr_score) +
            (0.15 * retention_score) +
            (0.10 * stability) +
            (0.05 * novelty)
        )
        
        # Causal Fragility risk adjustment factor:
        sources_count = len(m.traffic_sources)
        source_multiplier = min(1.0, sources_count / 3.0)
        volatility_multiplier = 1.0 - m.volatility_index
        
        self.reward_score = round(raw_score * source_multiplier * volatility_multiplier, 3)
        return self.reward_score

def calculate_organic_reward(metrics: Any, qualified_reach: float) -> float:
    """
    Fase 1: Otimiza pela Atenção do Público e Retenção Virulenta.
    - 35% Qualified Reach (Público de alta intenção)
    - 25% CTR
    - 20% Saves
    - 10% Shares
    - 10% Retenção (se disponível, ou interações adicionais)
    """
    w_reach = 0.35
    w_ctr = 0.25
    w_saves = 0.20
    w_shares = 0.10
    w_retention = 0.10
    
    # Normalização fictícia rápida para manter as métricas entre 0 e 1 (Apenas para o Simulador)
    norm_reach = min(qualified_reach / 100000.0, 1.0)
    norm_saves = min(getattr(metrics, 'saves', 0) / 1000.0, 1.0)
    norm_shares = min(getattr(metrics, 'shares', 0) / 500.0, 1.0)
    
    raw_reward = (norm_reach * w_reach) + (getattr(metrics, 'ctr', 0) * w_ctr) + (norm_saves * w_saves) + (norm_shares * w_shares) + (getattr(metrics, 'retention_3s', 0) * w_retention)
    return round(raw_reward, 3)

def calculate_economic_reward(metrics: Any, conversion_rate: float, margin: float, roas: float, risk_penalty: float) -> float:
    """
    Fase 2: Otimiza pelo Capital Puro.
    - 35% Profit Margin
    - 25% ROAS
    - 20% Conversion Rate (LTV proxy local)
    - 10% CTR
    - 10% Retention
    """
    w_profit = 0.35
    w_roas = 0.25
    w_conv = 0.20
    w_ctr = 0.10
    w_ret = 0.10
    
    norm_roas = min(roas / 5.0, 1.0) # ROAS 5.0 = cap
    norm_margin = min(margin / 100.0, 1.0)
    
    raw_reward = (norm_margin * w_profit) + (norm_roas * w_roas) + (conversion_rate * w_conv) + (getattr(metrics, 'ctr', 0) * w_ctr) + (getattr(metrics, 'retention_3s', 0) * w_ret)
    
    adjusted_reward = raw_reward * (1.0 - risk_penalty)
    return round(adjusted_reward, 3)

class CreativeGenome(BaseModel):
    hook: Dict[str, Any]
    psychology: Dict[str, Any]
    structure: Dict[str, Any]
    audience: Dict[str, Any]
    visual_language: Dict[str, Any]

class ExperimentPolicy(BaseModel):
    max_daily_posts: int = 3
    max_failed_assets: int = 5
    require_quality_gate: bool = True
    max_daily_generation_cost: float = 2.0
    max_monthly_api_cost: float = 20.0
    min_confidence_to_publish: float = 0.7
    cooldown_after_failure_seconds: int = 3600
