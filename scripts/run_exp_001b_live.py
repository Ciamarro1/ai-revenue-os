import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.revenue_os.analytics.schemas import ExperimentPolicy
from src.revenue_os.analytics.policy import PolicyEngine
from src.reality.base import CapabilityRegistry
from src.factory.base import FactoryRegistry
from src.reality.research.openmanus_provider import OpenManusProvider
from src.reality.social.pinterest.browser import PinterestBrowserProvider
from src.factory.video.moneyprinterturbo.adapter import MoneyPrinterTurboProvider
from src.services.experiment_runner import ExperimentRunner, ExperimentState
# from integrations.pinterest import PinterestAdapter 

def run_live():
    print("[EXP-001B] Iniciando Lote LIVE com Control Group (Pinterest API)")
    
    db = ExperimentDatabase()
    hypo_registry = HypothesisRegistry(db)
    reality_registry = CapabilityRegistry()
    reality_registry.register_research_provider(OpenManusProvider())
    reality_registry.register_publisher(PinterestBrowserProvider())
    
    factory_registry = FactoryRegistry()
    mpt_dir = Path(r"C:\Users\WDAGUtilityAccount\Downloads\ai rev\MoneyPrinterTurbo")
    factory_registry.register_video_generator(MoneyPrinterTurboProvider(mpt_dir))
    
    policy = ExperimentPolicy(
        max_daily_posts=3,
        max_daily_generation_cost=2.0,
        require_quality_gate=True
    )
    policy_engine = PolicyEngine(db, policy)
    
    runner = ExperimentRunner(
        db=db,
        registry=hypo_registry,
        reality_registry=reality_registry,
        factory_registry=factory_registry,
        policy_engine=policy_engine,
        require_human_approval=True
    )
    
    # 1. Variant A: Genome Vencedor Previsto
    print("\n--- Variante A: Genome Vencedor Previsto (Otimizado) ---")
    runner.ctx = {"variant_type": "A", "strategy": "winner_genome"} 
    try:
        res = runner.run_cycle(stop_at_state=ExperimentState.HUMAN_APPROVED)
        print(f"Status Variante A: {res.get('status')} | {res.get('error', '')}")
    except Exception as e:
        print(f"Erro Variante A: {e}")

    # 2. Variant B: Exploração Aleatória
    print("\n--- Variante B: Exploração Aleatória (Mutação Estocástica) ---")
    runner.ctx = {"variant_type": "B", "strategy": "random_exploration"}
    try:
        res = runner.run_cycle(stop_at_state=ExperimentState.HUMAN_APPROVED)
        print(f"Status Variante B: {res.get('status')} | {res.get('error', '')}")
    except Exception as e:
        print(f"Erro Variante B: {e}")

    # 3. Variant C: Baseline Humano (Controle)
    print("\n--- Variante C: Baseline Humano (Grupo de Controle) ---")
    runner.ctx = {"variant_type": "C", "strategy": "human_baseline"}
    try:
        res = runner.run_cycle(stop_at_state=ExperimentState.HUMAN_APPROVED)
        print(f"Status Variante C: {res.get('status')} | {res.get('error', '')}")
    except Exception as e:
        print(f"Erro Variante C: {e}")

if __name__ == "__main__":
    run_live()
