import pytest
from src.services.revenue_simulator import RevenueSimulator
from src.revenue_os.analytics.metrics_engine import MetricsEngine
from src.revenue_os.analytics.decision_engine import DecisionEngine

@pytest.fixture
def simulator():
    return RevenueSimulator()

@pytest.fixture
def metrics_engine():
    return MetricsEngine()

@pytest.fixture
def decision_engine():
    return DecisionEngine()

def test_trade_off_hybrid_wins(simulator, metrics_engine, decision_engine):
    """
    Simula o cenário A vs B vs C.
    Comprova que A gera impressões vazias.
    B gera alta conversão mas o algoritmo esmaga o alcance.
    C acha o sweet spot e ganha.
    """
    profiles = {
        "A": "attention_first",
        "B": "commercial",
        "C": "hybrid"
    }
    
    # Gerando os dados de funil
    exps = simulator.simulate_economic_funnel("finance", 100000, profiles, 30)
    
    # Agrupando lucros e alcances para inspeção no teste
    profits = {"A": 0, "B": 0, "C": 0}
    impressions = {"A": 0, "B": 0, "C": 0}
    
    for e in exps:
        profits[e.variant.id] += e.real_world_metrics.profit_usd
        impressions[e.variant.id] += e.real_world_metrics.impressions
        
    print(f"\n[A - Attention] Imps: {impressions['A']} | Profit: ${profits['A']:.2f}")
    print(f"[B - Hard Sell] Imps: {impressions['B']} | Profit: ${profits['B']:.2f}")
    print(f"[C - Hybrid   ] Imps: {impressions['C']} | Profit: ${profits['C']:.2f}")
    
    # A Híbrida deve lucrar mais que a 'Attention First' (que converte lixo) 
    # e mais que a 'Hard Sell' (que perde distribuição e morre cedo).
    assert profits["C"] > profits["A"]
    assert profits["C"] > profits["B"]
    
    # Validando o Decision Engine Gate (Passando os dados da C)
    report = {
        "sample_size_total": impressions["C"], # Mercado total alcançado
        "confidence": 0.96,
        "winner": "C",
        "winner_profit": profits["C"] / 30, # Lucro médio por experimento
        "winner_impressions": impressions["C"]
    }
    
    decision = decision_engine.evaluate_experiment(report, minimum_sample=1000, baseline_profit=10.0)
    
    # Se ela lucrar o suficiente e mantiver o mercado
    assert decision["decision"] in ["SCALE", "ITERATE"]
    
def test_hard_sell_dies_in_distribution(simulator, metrics_engine, decision_engine):
    profiles = {"B": "commercial"}
    exps = simulator.simulate_economic_funnel("finance", 100000, profiles, 10)
    
    avg_impressions = sum([e.real_world_metrics.impressions for e in exps]) / 10
    
    # O perfil commercial deve ser estrangulado pelo algoritmo
    # O baseline era 100k, ele deve ficar entre 10k e 40k.
    assert avg_impressions < 50000
    
    report = {
        "sample_size_total": avg_impressions * 10,
        "confidence": 0.99,
        "winner": "B",
        "winner_profit": 5000.0, # Mesmo lucrando muito
        "winner_impressions": avg_impressions # O mercado é minúsculo
    }
    
    decision = decision_engine.evaluate_experiment(report, minimum_sample=1000, baseline_profit=10.0)
    
    # O engine de decisão NÃO deve permitir "SCALE" se o mercado (impressões isoladas) não passar do mínimo.
    assert decision["decision"] != "SCALE"

def test_risk_adjustment_factor():
    from src.revenue_os.analytics.schemas import RealWorldMetrics, ExperimentContract
    
    # Testando o cálculo de reward nativo com métricas forjadas
    exp = ExperimentContract(
        experiment_id="TEST-RISK",
        hypothesis={"statement": "Testing fragility", "metric_target": "profit_usd"},
        variant={"id": "FRAGILE", "description": "Lucra mas é instável"},
        economics={"generation_cost_usd": 1.0, "revenue_usd": 1000.0},
        creative_hash="hash"
    )
    
    # Preenchemos com lucro brutal
    exp.real_world_metrics.impressions = 100000
    exp.real_world_metrics.ctr_percent = 5.0
    exp.real_world_metrics.landing_visit_percent = 50.0
    exp.real_world_metrics.conversion_count = 500
    exp.real_world_metrics.profit_usd = 2000.0
    
    # Caso 1: Variante Segura (Multi-fonte, Baixa Volatilidade)
    exp.real_world_metrics.traffic_sources = ["youtube", "tiktok", "pinterest"]
    exp.real_world_metrics.volatility_index = 0.2
    safe_reward = exp.calculate_reward()
    
    # Caso 2: Variante Frágil (1 Fonte, Alta Volatilidade)
    exp.real_world_metrics.traffic_sources = ["youtube"]
    exp.real_world_metrics.volatility_index = 0.8
    fragile_reward = exp.calculate_reward()
    
    print(f"\n[Safe Reward]: {safe_reward} | [Fragile Reward]: {fragile_reward}")
    
    # A Fragilidade Causal deve punir o Score duramente
    assert fragile_reward < safe_reward * 0.5
