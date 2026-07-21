import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.reality.base import CapabilityRegistry
from src.factory.base import FactoryRegistry
from src.reality.research.openmanus_provider import OpenManusProvider
from src.factory.video.moneyprinterturbo.adapter import MoneyPrinterTurboProvider
from src.factory.video.movielite.adapter import MovieLiteProvider
from src.services.experiment_runner import ExperimentRunner, ExperimentState

def run_shadow():
    print("[EXP-001A] Iniciando Experimento SHADOW MODE (Dry Run)")
    
    db = ExperimentDatabase("prod_db.sqlite3")
    hypo_registry = HypothesisRegistry(db)
    
    # 1. Reality Layer (Apenas Pesquisa, sem Publisher real para não postar)
    reality_registry = CapabilityRegistry()
    reality_registry.register_research_provider(OpenManusProvider())
    
    # 2. Factory Layer (Geração Real de Vídeo via MPT e MovieLite)
    factory_registry = FactoryRegistry()
    mpt_dir = Path(r"C:\Users\WDAGUtilityAccount\Downloads\ai rev\MoneyPrinterTurbo")
    factory_registry.register_video_generator(MoneyPrinterTurboProvider(mpt_dir))
    factory_registry.register_video_generator(MovieLiteProvider())
    
    # 3. Runner
    runner = ExperimentRunner(
        db=db,
        registry=hypo_registry,
        reality_registry=reality_registry,
        factory_registry=factory_registry
    )
    
    # Executa até a fase de Quality Check (antes de publicar)
    print("Executando pipeline ate QUALITY_CHECKED...")
    res = runner.run_cycle(stop_at_state=ExperimentState.QUALITY_CHECKED)
    
    print("\\n=======================================================")
    if res["status"] == "success":
        print(f"SUCESSO SHADOW MODE!")
        print(f"Estado Final: {res['final_state']}")
        print(f"Experimento: {res['experiment_id']}")
        print(f"O Video foi gerado e passou na checagem de qualidade, sem ser publicado no Pinterest.")
    else:
        print(f"FALHA NO CICLO: {res.get('error')}")
        print(f"Estado que falhou: {res.get('step')}")
    print("=======================================================")

if __name__ == "__main__":
    run_shadow()
