from src.revenue_os.plugins.learning.engine import ProductionLearningEngine

def test_learning_engine_ignores_benchmarks():
    engine = ProductionLearningEngine()
    
    # Entradas de Benchmark e Teste Local apenas
    benchmark_entries = [
        {"metric_source": "SIMULATED_BENCHMARK", "event_type": "BENCHMARK"},
        {"classification_status": "LOCAL_TEST", "event_type": "TEST"}
    ]
    
    res = engine.run_cycle(custom_entries=benchmark_entries)
    
    assert res.total_ledger_entries == 2
    assert res.real_production_entries == 0
    assert res.ignored_benchmark_entries == 2
    assert res.weights_recalibrated == 0

def test_learning_engine_updates_on_real_production():
    engine = ProductionLearningEngine()
    
    # Entradas de Produção Real
    real_entries = [
        {"metric_source": "REAL_PRODUCTION", "event_type": "SALE_CONFIRMED"},
        {"classification_status": "REAL_PRODUCTION", "event_type": "CONVERSION_TRACKED"}
    ]
    
    res = engine.run_cycle(custom_entries=real_entries)
    
    assert res.total_ledger_entries == 2
    assert res.real_production_entries == 2
    assert res.ignored_benchmark_entries == 0
    assert res.weights_recalibrated > 0
    
    weights = engine.get_weights()
    for w in weights:
        assert w["current_weight"] > w["previous_weight"]
        assert w["delta"] > 0
