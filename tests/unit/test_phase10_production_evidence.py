import pytest
from src.revenue_os.observability.production_evidence_evaluator import ProductionEvidenceEvaluator

def test_production_evidence_evaluator_benchmark_vs_production():
    evaluator = ProductionEvidenceEvaluator()

    # Teste 1: Benchmark Simulado
    sim_res = evaluator.evaluate_production_evidence(metric_source="SIMULATED_BENCHMARK")
    assert sim_res["is_real_production_verified"] is False
    assert sim_res["edd_verdict"] == "MODO_HOMOLOGACAO_AGUARDANDO_DISPARO"

    # Teste 2: Produção Real com 1 Clique e 1 Comissão
    prod_res = evaluator.evaluate_production_evidence(
        metric_source="REAL_PRODUCTION",
        confirmed_revenue_usd=25.0,
        confirmed_clicks=15
    )
    assert prod_res["is_real_production_verified"] is True
    assert prod_res["milestones"]["PE-1_first_asset_published"]["verified"] is True
    assert prod_res["milestones"]["PE-2_first_click_confirmed"]["verified"] is True
    assert prod_res["milestones"]["PE-3_first_commission_confirmed"]["verified"] is True
    assert prod_res["completed_milestones_count"] == 3
    assert prod_res["edd_verdict"] == "EVIDENCIAS_DE_PRODUCAO_VALIDADAS"
