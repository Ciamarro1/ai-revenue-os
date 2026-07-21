import pytest
import os
from src.revenue_os.observability.decision_ledger import DecisionLedger
from src.revenue_os.analytics.calibration_engine import CalibrationEngine

def test_decision_ledger_persistence():
    log_file = "test_decisions.jsonl"
    if os.path.exists(log_file):
        os.remove(log_file)
        
    ledger = DecisionLedger(log_path=log_file)
    
    # Gravando duas decisões
    ledger.record_decision("EXP-VP-001", "INVEST", ["Confidence Alta"])
    ledger.record_decision("EXP-VP-002", "EXIT", ["Lucro Negativo"])
    
    # Lendo o arquivo e validando integridade do JSONL
    history = ledger.read_history()
    
    assert len(history) == 2
    assert history[0]["experiment"] == "EXP-VP-001"
    assert history[1]["decision"] == "EXIT"
    assert "timestamp" in history[0]
    
    # Limpando
    if os.path.exists(log_file):
        os.remove(log_file)

def test_calibration_engine():
    engine = CalibrationEngine()
    
    # O Simulador estimou Reward de 0.81 (Extremamente lucrativo)
    # A Realidade devolveu apenas 0.40. O erro é gigante (0.41).
    delta = engine.calculate_calibration_error(0.81, 0.40)
    
    assert delta["calibration_error"] == 0.41
    assert delta["status"] == "DANGEROUS_DEVIATION"
    assert delta["action_required"] == "RECALIBRATE_SIMULATOR"
    
    # Ao recalibrar o Risk Factor
    # Se o fator de risco atual era 1.0 (Seguro), a punição histórica corta ele para baixo
    novo_risco = engine.adjust_risk_factor(1.0, error_history_avg=0.41)
    
    # O novo fator de risco base será achatado para 0.59
    assert novo_risco == 0.59

def test_calibration_drift():
    engine = CalibrationEngine()
    
    # VP-001: O Simulador jurava que o CTR ia ser 4.8%. Mas na prática foi 3.7%.
    drift = engine.calculate_predictive_bias("CTR", predicted=4.8, reality=3.7)
    
    assert drift["metric"] == "CTR"
    # 3.7 / 4.8 = 0.77
    assert drift["correction_multiplier"] == 0.77
    assert "Superestimou" in drift["trend"]
    
    # Próxima previsão do Simulador (Digamos que ele gerou 5.0).
    # Como ele tem um histórico de superestimar em 23%, nós aplicamos o fator:
    nova_predicao = 5.0 * drift["correction_multiplier"]
    
    assert nova_predicao == 3.85 # Agora a predição está calibrada para a dura realidade!

def test_contextual_calibration():
    engine = CalibrationEngine()
    
    # VP-001 (Etapa 2): Erro no nicho de finanças não deve interferir no nicho de produtividade.
    drift_finance = engine.calculate_predictive_bias("CTR", predicted=5.0, reality=2.5, context_key="finance")
    drift_prod = engine.calculate_predictive_bias("CTR", predicted=4.0, reality=3.9, context_key="productivity")
    
    assert drift_finance["context_key"] == "finance"
    assert drift_finance["correction_multiplier"] == 0.50 # Caiu pela metade (Superestimou brutalmente)
    
    assert drift_prod["context_key"] == "productivity"
    assert drift_prod["correction_multiplier"] == 0.98 # Quase perfeito
    assert "Equilibrado" in drift_prod["trend"]

from src.mcp.health_monitor import HealthMonitor
from src.mcp.registry import CapabilityRegistry, MCPRegistry

def test_mcp_circuit_breaker():
    base_mcp = MCPRegistry()
    monitor = HealthMonitor()
    
    # Instanciamos o Registry acoplado ao monitor de saúde
    cap_registry = CapabilityRegistry(base_mcp, monitor)
    cap_registry.map_capability("publish_short_video", ["PinterestServer", "YouTubeServer"])
    
    # Derrubamos a API do Pinterest na força bruta
    monitor.trigger_rate_limit("PinterestServer")
    
    # Se testarmos e pedirmos o Pinterest de preferência, ele vai dar Circuit Breaker
    # e fará fallback para o YouTube (se o YouTube estiver registrado na base_mcp).
    # Aqui, para teste unitário simples, apenas validamos o Circuit Breaker aberto global
    # quando derrubamos ambos.
    monitor.trigger_rate_limit("YouTubeServer")
    
    with pytest.raises(RuntimeError) as excinfo:
        cap_registry.execute_capability("publish_short_video")
        
    assert "Circuit Breaker Aberto" in str(excinfo.value)

from src.revenue_os.analytics.scoreboard import Scoreboard
from src.services.shadow_mode_runner import ShadowModeRunner

def test_shadow_mode_scoreboard_baseline():
    board = Scoreboard()
    
    # O Sistema Quantitativo apostou $800 na variante A, e $200 na B.
    ai_allocations = {"A": 800.0, "B": 200.0, "C": 0.0}
    
    # Realidade (ROI): A rendeu 2.0x (100% lucro). B rendeu 0.5 (Prejuízo). C rendeu 1.1x.
    real_profits = {"A": 2.0, "B": 0.5, "C": 1.1}
    # CTR Anterior para a heurística cega "Max CTR" apostar tudo na C.
    ctrs = {"A": 0.03, "B": 0.02, "C": 0.09} 
    
    board.evaluate_cycle(1000.0, ai_allocations, real_profits, ctrs)
    summary = board.get_summary()
    
    # AI Ganho = (800 * 2) + (200 * 0.5) = 1600 + 100 = 1700
    assert summary["AI_OS_Profit"] == 1700.0
    
    # Equal Ganho = (333.3 * 2) + (333.3 * 0.5) + (333.3 * 1.1) = ~1200
    assert summary["Equal_Baseline_Profit"] < 1300.0
    
    # Max CTR Ganho = Apostou os 1000 na C (rendeu 1.1) = 1100
    assert summary["MaxCTR_Baseline_Profit"] == 1100.0
    
def test_shadow_mode_security_lock():
    runner = ShadowModeRunner()
    
    # Garantir que a trava fatal existe. O Fundo em Shadow Mode jamais operará capital.
    with pytest.raises(RuntimeError) as excinfo:
        runner.execute_publish_action()
        
    assert "FATAL" in str(excinfo.value)
    assert "WRITE" in str(excinfo.value)

from src.revenue_os.analytics.schemas import calculate_organic_reward, calculate_economic_reward
from src.revenue_os.analytics.resource_allocator import ResourceAllocator, ResourceType, AllocationMode
from pydantic import BaseModel

class DummyMetrics(BaseModel):
    saves: int = 0
    shares: int = 0
    ctr: float = 0.0
    retention_3s: float = 0.0

def test_organic_vs_economic_dual_reward():
    # Vídeo puramente viral (Muitos saves, shares, zero vendas)
    viral_metrics = DummyMetrics(saves=1000, shares=500, ctr=0.08, retention_3s=0.70)
    
    # 1. No Modo Orgânico, o Reward dele vai ao teto.
    organic_reward = calculate_organic_reward(viral_metrics, qualified_reach=100000.0)
    # NormSaves(1.0)*0.20 + NormShares(1.0)*0.10 + Reach(1.0)*0.35 + Ctr(0.08)*0.25 + Ret(0.70)*0.10
    # = 0.20 + 0.10 + 0.35 + 0.02 + 0.07 = 0.74 (Extremamente Alto)
    assert organic_reward > 0.70
    
    # 2. No Modo Pago, o vídeo viral SEM VENDA naufraga (Prejuízo massivo).
    # Margin = 0, ROAS = 0, Conversion Rate = 0
    economic_reward = calculate_economic_reward(viral_metrics, conversion_rate=0.0, margin=0.0, roas=0.0, risk_penalty=0.0)
    # Apenas ganha pontuação pelo CTR(0.08)*0.10 + Retenção(0.70)*0.10 = 0.078
    assert economic_reward < 0.10
    
def test_resource_allocator_organic_mode():
    allocator = ResourceAllocator(mode=AllocationMode.ORGANIC_DISCOVERY)
    
    # Variante A é o Genoma Viral. Variante B é lixo.
    candidates = {"Genoma_Viral": 0.85, "Genoma_Ruim": 0.12}
    
    # O "Capital" aqui é a quantidade de publicações que a GPU pode gerar (30 posts).
    allocations = allocator.allocate(resource_pool=30.0, resource_type=ResourceType.POST_QUOTA, candidates=candidates)
    
    # Exploração vs Explotação.
    # Top half (Genoma_Viral) leva 70% da cota (21 posts).
    assert allocations["Genoma_Viral"] == 21.0
    assert allocations["Genoma_Ruim"] == 9.0

from src.revenue_os.analytics.genome_library import GenomeLibrary
import os

def test_genome_library_success_rate():
    # Cria BD temporario para teste
    test_db = "test_genome_db.jsonl"
    if os.path.exists(test_db):
        os.remove(test_db)
        
    library = GenomeLibrary(db_path=test_db)
    
    # Simula experimento 1 com Genoma A (Sucesso Orgânico Massivo)
    library.extract_and_catalog("Genome_023_Curiosity", {"hook": "Curiosity", "emotion": "Urgency"}, reward=0.85)
    
    # Simula experimento 2 com mesmo Genoma A (Sucesso)
    library.extract_and_catalog("Genome_023_Curiosity", {"hook": "Curiosity", "emotion": "Urgency"}, reward=0.72)
    
    # Simula experimento 3 com mesmo Genoma A (Falha Orgânica)
    library.extract_and_catalog("Genome_023_Curiosity", {"hook": "Curiosity", "emotion": "Urgency"}, reward=0.40)
    
    # O Padrão ocorreu 3 vezes e teve sucesso 2 vezes. Success Rate = 66%
    entry = library.catalog["Genome_023_Curiosity"]
    assert entry["sample_size"] == 3
    assert entry["wins"] == 2
    assert round(entry["success_rate"], 2) == 0.67 # Arredondado 2/3
    
    if os.path.exists(test_db):
        os.remove(test_db)

def test_discovery_velocity_metric():
    board = Scoreboard()
    
    # Rodei 4 ciclos de experimento pra achar o Genoma 1
    board.evaluate_cycle(100.0, {}, {}, {}) # Ciclo 1
    board.evaluate_cycle(100.0, {}, {}, {}) # Ciclo 2
    board.evaluate_cycle(100.0, {}, {}, {}) # Ciclo 3
    board.evaluate_cycle(100.0, {}, {}, {}) # Ciclo 4
    board.register_pattern_discovery() # Ocorreu no ciclo 4. Média = 4.0
    
    assert board.get_summary()["Discovery_Velocity_Cycles"] == 4.0
    assert board.get_summary()["Patterns_Cataloged"] == 1
    
    # Rodei mais 2 ciclos pra achar o Genoma 2. (4 + 2) / 2 = 3.0 de média.
    board.evaluate_cycle(100.0, {}, {}, {}) # Ciclo 5
    board.evaluate_cycle(100.0, {}, {}, {}) # Ciclo 6
    board.register_pattern_discovery() 
    
    assert board.get_summary()["Discovery_Velocity_Cycles"] == 3.0
    assert board.get_summary()["Patterns_Cataloged"] == 2
