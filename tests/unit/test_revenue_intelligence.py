import pytest
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.learning.reward_model import RewardModel
from src.revenue_os.learning.portfolio_optimizer import PortfolioOptimizer
from src.revenue_os.learning.strategy_engine import StrategyEngine

def test_reward_model():
    model = RewardModel()
    # Caso 1: Performance perfeita (deve dar score 100.0)
    reward_max = model.calculate_reward(revenue_usd=50.0, ctr_percent=5.0, retention_3s_percent=60.0)
    assert reward_max == 100.0
    
    # Caso 2: Performance fraca (só sinal inicial de retenção)
    reward_low = model.calculate_reward(revenue_usd=0.0, ctr_percent=0.5, retention_3s_percent=10.0)
    assert reward_low < 10.0

def test_portfolio_optimizer():
    variants = [
        {"variant_id": "A_Curiosity", "conversion_count": 25, "impressions": 100},
        {"variant_id": "B_Benefit", "conversion_count": 2, "impressions": 100}
    ]
    # Executa a otimização de Thompson Sampling com orçamento virtual de $1000
    allocations = PortfolioOptimizer.allocate_budgets(variants, total_budget=1000.0)
    
    assert "A_Curiosity" in allocations
    assert "B_Benefit" in allocations
    # A soma das alocações deve ser exatamente $1000 (com margem de arredondamento)
    assert abs(sum(allocations.values()) - 1000.0) < 0.1

def test_strategy_engine_loop_in_memory():
    # Setup de banco isolado em memória
    db = ExperimentDatabase(":memory:")
    
    conn = db._get_conn()
    c = conn.cursor()
    
    # Insere dados de sucesso
    c.execute("INSERT INTO hypotheses (id, statement, category, status) VALUES (10, 'O segredo de investir em ações', 'finance', 'testing')")
    c.execute("INSERT INTO experiments (experiment_id, hypothesis_id, variant_id, revenue_usd, generation_cost_usd) VALUES ('EXP-OK', 10, 'A', 80.0, 5.0)")
    c.execute("INSERT INTO metrics (experiment_id, impressions, conversion_count, reward_score, ctr_percent, retention_3s_percent) VALUES ('EXP-OK', 1000, 50, 95.0, 5.0, 65.0)")
    
    # Insere dados de falha
    c.execute("INSERT INTO hypotheses (id, statement, category, status) VALUES (20, 'compre esse e-book rápido', 'sales', 'testing')")
    c.execute("INSERT INTO experiments (experiment_id, hypothesis_id, variant_id, revenue_usd, generation_cost_usd) VALUES ('EXP-FAIL', 20, 'B', 0.0, 10.0)")
    c.execute("INSERT INTO metrics (experiment_id, impressions, conversion_count, reward_score, ctr_percent, retention_3s_percent) VALUES ('EXP-FAIL', 500, 1, 2.0, 0.2, 5.0)")
    
    conn.commit()
    
    # Executa o loop evolutivo
    engine = StrategyEngine(db)
    evolved = engine.run_learning_cycle("marketing digital")
    
    # Validações
    assert evolved["statement"] is not None
    assert isinstance(evolved["statement"], str)
    # Deve carregar a categoria de maior peso (neste caso, 'finance')
    assert evolved["category"] == "finance"
    
    # Garante que a nova hipótese foi salva no banco
    c.execute("SELECT statement FROM hypotheses WHERE statement = ?", (evolved["statement"],))
    inserted = c.fetchone()
    assert inserted is not None
    assert inserted[0] == evolved["statement"]
