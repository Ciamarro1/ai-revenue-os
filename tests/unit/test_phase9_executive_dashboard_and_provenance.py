import pytest
from src.revenue_os.observability.live_dashboard import LiveOperationsDashboard
from src.revenue_os.observability.executive_dashboard import ExecutiveCommandCenter

def test_live_dashboard_metric_source_provenance():
    dashboard = LiveOperationsDashboard()
    
    # 1. Teste com benchmark simulado
    sim_res = dashboard.get_live_dashboard_metrics(metric_source="SIMULATED_BENCHMARK")
    assert sim_res["metric_source"] == "SIMULATED_BENCHMARK"
    assert sim_res["is_verified_real_production"] is False
    assert sim_res["edd_validation"]["pm_milestones_proven"] is False

    # 2. Teste com produção real verificada
    prod_res = dashboard.get_live_dashboard_metrics(metric_source="REAL_PRODUCTION")
    assert prod_res["metric_source"] == "REAL_PRODUCTION"
    assert prod_res["is_verified_real_production"] is True
    assert prod_res["edd_validation"]["pm_milestones_proven"] is True

def test_executive_command_center_rendering():
    ecc = ExecutiveCommandCenter()
    res = ecc.render_executive_command_center(metric_source="REAL_PRODUCTION")

    assert res["executive_summary"]["is_live_production"] is True
    assert res["revenue"]["last_30_days_usd"] == 310.00
    assert res["costs"]["net_profit_usd"] > 0
    assert res["next_suggested_experiment"]["is_approved"] is True
