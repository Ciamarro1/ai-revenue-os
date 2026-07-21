import pytest
from src.reality.research.autonomous_engine import AutonomousResearchEngine
from src.revenue_os.analytics.genome_library import Genome
from src.revenue_os.portfolio_manager import PortfolioManager
from src.revenue_os.scheduler import DaemonScheduler
from src.revenue_os.simulation.reality_simulator import RealitySimulator

def test_autonomous_research_live_data(tmp_path):
    engine = AutonomousResearchEngine(output_dir=tmp_path)
    candidates = engine.discover_topic_candidates("productivity")
    assert len(candidates) >= 2
    assert candidates[0].topic is not None
    assert candidates[0].score > 0

def test_genome_adaptive_scoring():
    genome = Genome(
        hook="Question Hook",
        emotion="Curiosity",
        visual_style="Bright",
        cta="Click link",
        ctr=0.06,
        save_rate=0.08,
        conversion_rate=0.04,
        revenue=35.0,
        observations_count=5
    )

    initial_weights = genome.get_adaptive_weights(total_system_samples=5)
    assert initial_weights["revenue"] == 0.15

    # Com 200 amostras acumuladas no sistema
    genome.observations_count = 200
    adapted_weights = genome.get_adaptive_weights(total_system_samples=200)
    assert adapted_weights["revenue"] > 0.15
    assert genome.score > 0

def test_portfolio_manager_constrained_optimization():
    manager = PortfolioManager()
    experiments = [
        {"id": "EXP-1", "expected_roi": 4.5, "confidence": 0.9, "gpu_hours": 2.0, "budget_usd": 15.0},
        {"id": "EXP-2", "expected_roi": 3.8, "confidence": 0.85, "gpu_hours": 1.5, "budget_usd": 10.0},
        {"id": "EXP-3", "expected_roi": 5.0, "confidence": 0.95, "gpu_hours": 6.0, "budget_usd": 40.0}, # GPU pesado
        {"id": "EXP-4", "expected_roi": 2.1, "confidence": 0.7, "gpu_hours": 1.0, "budget_usd": 5.0}
    ]

    opt = manager.optimize_constrained_portfolio(
        experiments,
        max_gpu_hours=4.0,
        max_budget_usd=30.0,
        max_posts=5
    )

    assert opt["total_selected"] >= 1
    assert opt["resource_utilization"]["used_gpu_hours"] <= 4.0
    assert opt["resource_utilization"]["used_budget_usd"] <= 30.0

def test_daemon_scheduler_24h_cycle():
    scheduler = DaemonScheduler()
    report = scheduler.run_24h_cycle("productivity")

    assert report["status"] == "24h_cycle_completed"
    assert len(report["executed_windows"]) == 5
    assert report["results"]["00:00"]["phase"] == "RESEARCH"
    assert report["results"]["22:00"]["phase"] == "REALLOCATION"

def test_reality_simulator_180_days():
    sim = RealitySimulator()
    res = sim.simulate_long_term_run(total_posts=10000, days=180)

    assert res["simulation_parameters"]["total_posts"] == 10000
    assert res["cumulative_results"]["gross_revenue_usd"] > 0
    assert res["cumulative_results"]["net_profit_usd"] > 0
    assert len(res["snapshots_every_30_days"]) == 6
