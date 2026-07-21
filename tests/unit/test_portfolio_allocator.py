import pytest
from src.services.portfolio_simulator import PortfolioSimulator
from src.revenue_os.analytics.portfolio_state import PortfolioAsset

def test_all_in_errado_prevention():
    # O sistema não deve botar 1000 num ativo só, mesmo que ele seja insano.
    assets = [
        PortfolioAsset(experiment_id="A_MEDIO", expected_profit=200, confidence=0.90, risk=0.1),
        PortfolioAsset(experiment_id="B_EXPLOSIVO", expected_profit=5000, confidence=0.70, risk=0.9),
    ]
    
    state = PortfolioSimulator.simulate_day_cycle(1000.0, assets)
    
    for asset in state.active_experiments:
        if asset.experiment_id == "B_EXPLOSIVO":
            # Teto é 30% do bolo (300)
            assert asset.allocation <= 300.0
            print(f"\n[B_EXPLOSIVO] Tentou All-In mas Motor segurou em: ${asset.allocation}")

def test_liquidacao_perda_cascata():
    # Se o lucro esperado cair abaixo de 0 ou confiança abaixo de 50%, Liquida (EXIT).
    assets = [
        PortfolioAsset(experiment_id="C_FALSO", expected_profit=-50, confidence=0.90, risk=0.5),
        PortfolioAsset(experiment_id="D_MORTO", expected_profit=100, confidence=0.40, risk=0.5),
    ]
    
    state = PortfolioSimulator.simulate_day_cycle(1000.0, assets)
    
    for asset in state.active_experiments:
        assert asset.status == "EXIT"
        assert asset.allocation == 0.0

def test_diversificacao_correta():
    assets = [
        # O A tem o melhor RAR (200 / 0.1 = 2000)
        PortfolioAsset(experiment_id="A_SEGURO", expected_profit=200, confidence=0.95, risk=0.1),
        # O B tem RAR menor (800 / 0.8 = 1000)
        PortfolioAsset(experiment_id="B_ARISCO", expected_profit=800, confidence=0.75, risk=0.8),
    ]
    
    state = PortfolioSimulator.simulate_day_cycle(1000.0, assets)
    
    allocations = {a.experiment_id: a.allocation for a in state.active_experiments}
    
    # Ambos recebem aporte.
    assert allocations["A_SEGURO"] > 0
    assert allocations["B_ARISCO"] > 0
    # E o Seguro não quebra o limite, recebendo o Teto da trancha
    assert allocations["A_SEGURO"] <= 300.0 
    print(f"\n[A_SEGURO]: ${allocations['A_SEGURO']} | [B_ARISCO]: ${allocations['B_ARISCO']}")
