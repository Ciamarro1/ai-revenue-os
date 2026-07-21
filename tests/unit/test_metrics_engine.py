import pytest
from src.services.experiment_simulator import SyntheticRealitySimulator
from src.revenue_os.analytics.metrics_engine import MetricsEngine
from src.agents.experiment_analyst import ExperimentAnalystAgent

@pytest.fixture
def simulator():
    return SyntheticRealitySimulator()

@pytest.fixture
def engine():
    return MetricsEngine()

@pytest.fixture
def analyst():
    return ExperimentAnalystAgent()

def test_clear_win(simulator, engine, analyst):
    # Causalidade de que A é muito melhor em retenção e não perde CTR
    exps = simulator.simulate_world_response(
        hypothesis_statement="Ganchos agressivos funcionam",
        metric_target="retention_3s",
        variant_a_desc="Agressivo",
        variant_b_desc="Normal",
        n_samples=60,
        causation_bias="A"
    )
    # Ajuste forçado para garantir que A vença e não tenha trade-off de CTR
    for e in exps:
        if e.variant.id == "A":
            e.real_world_metrics.retention_3s_percent += 50.0
            e.real_world_metrics.ctr_percent += 5.0
        else:
            e.real_world_metrics.retention_3s_percent = 10.0
            e.real_world_metrics.ctr_percent = 2.0
            
    report = engine.analyze_ab_test(exps)
    conclusion = analyst.analyze_results(report)
    
    assert report["is_significant"] == True
    assert report["winner"] == "A"
    assert report["trade_off_detected"] == False
    assert "A validated" in conclusion

def test_tie(simulator, engine, analyst):
    # Ambas as variantes performam identicamente
    exps = simulator.simulate_world_response(
        hypothesis_statement="Testando fontes",
        metric_target="retention_3s",
        variant_a_desc="Arial",
        variant_b_desc="Roboto",
        n_samples=100
    )
    for e in exps:
        e.real_world_metrics.retention_3s_percent = 25.0
        
    report = engine.analyze_ab_test(exps)
    conclusion = analyst.analyze_results(report)
    
    assert report["is_significant"] == False
    assert report["winner"] is None
    assert "No statistically significant winner" in conclusion

def test_small_sample(simulator, engine, analyst):
    # Apenas 5 experimentos
    exps = simulator.simulate_world_response(
        hypothesis_statement="Ganchos",
        metric_target="retention_3s",
        variant_a_desc="A",
        variant_b_desc="B",
        n_samples=5
    )
    report = engine.analyze_ab_test(exps)
    conclusion = analyst.analyze_results(report)
    
    # O LLM Analyst barra imediatamente
    assert "Insufficient evidence" in conclusion

def test_trade_off(simulator, engine, analyst):
    # Variante A ganha retenção brutalmente, mas o CTR afunda.
    exps = simulator.simulate_world_response(
        hypothesis_statement="Thumbnails limpas",
        metric_target="retention_3s",
        variant_a_desc="Limpa",
        variant_b_desc="Poluída",
        n_samples=100,
        causation_bias="A"
    )
    
    for e in exps:
        if e.variant.id == "A":
            e.real_world_metrics.retention_3s_percent = 60.0 # Vence na métrica principal
            e.real_world_metrics.ctr_percent = 1.0 # Perde brutalmente no CTR secundário
        else:
            e.real_world_metrics.retention_3s_percent = 20.0
            e.real_world_metrics.ctr_percent = 10.0 # Vence no secundário
            
    report = engine.analyze_ab_test(exps)
    conclusion = analyst.analyze_results(report)
    
    assert report["is_significant"] == True
    assert report["winner"] == "A"
    assert report["trade_off_detected"] == True
    assert "Trade-off detected" in conclusion

def test_simpsons_paradox(simulator, engine, analyst):
    import random
    random.seed(42)
    exps = simulator.simulate_world_response(
        hypothesis_statement="Testando Viés Global",
        metric_target="retention_3s",
        variant_a_desc="Global Winner",
        variant_b_desc="Local Winner",
        n_samples=90,
        causation_bias="A",
        simpson_paradox=True
    )
    
    # O motor global acusa A como vencedor
    report_global = engine.analyze_ab_test(exps)
    assert report_global["winner"] == "A"
    
    # Porém, nos nichos isolados, B amassa A (O Causal Guard)
    exps_finance = [e for e in exps if "[Niche: finance]" in e.variant.description]
    report_finance = engine.analyze_ab_test(exps_finance)
    assert report_finance["winner"] == "B"

def test_saturation_decay(simulator, engine):
    # Semana 1 (Audiência Fresca)
    exps_week1 = simulator.simulate_world_response(
        hypothesis_statement="Hook X Saturation",
        metric_target="ctr",
        variant_a_desc="Hook X",
        variant_b_desc="Normal",
        n_samples=50,
        causation_bias="A",
        exposure_count=1000,
        audience_pool=1000000
    )
    
    # Semana 10 (Audiência Fadigada: 900 mil expostos)
    exps_week10 = simulator.simulate_world_response(
        hypothesis_statement="Hook X Saturation",
        metric_target="ctr",
        variant_a_desc="Hook X",
        variant_b_desc="Normal",
        n_samples=50,
        causation_bias="A",
        exposure_count=900000,
        audience_pool=1000000
    )
    
    report_w1 = engine.analyze_ab_test(exps_week1)
    report_w10 = engine.analyze_ab_test(exps_week10)
    
    # O CTR médio da Variante A deve despencar na Semana 10 (Fadiga Exponencial)
    mean_a_w1 = report_w1["variants"]["A"]["mean"]
    mean_a_w10 = report_w10["variants"]["A"]["mean"]
    
    assert mean_a_w10 < mean_a_w1 * 0.5 # Caiu mais de 50% devido à fadiga
