import sys, time, os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.revenue_os.analytics.profile import ExperimentProfile
from src.services.experiment_runner import ExperimentRunner, ExperimentState
# Config real or mocked registries
from src.factory.base import FactoryRegistry
from src.reality.base import CapabilityRegistry
from src.factory.video.moneyprinterturbo.adapter import MoneyPrinterTurboProvider
from src.reality.research.stochastic_provider import StochasticResearchProvider
from src.revenue_os.analytics.genome_library import GenomeLibrary

def burn_in():
    print("=== BURN-IN TEST (EXP-001A.9) ===")
    print("Duração: 24h. 1 Vídeo a cada 5 minutos.")
    
    db = ExperimentDatabase("prod_db.sqlite3")
    hypo = HypothesisRegistry(db)
    profile = ExperimentProfile("config/experiment_profile.yaml")
    
    factory = FactoryRegistry()
    mpt_dir = Path(__file__).parent.parent / "MoneyPrinterTurbo"
    factory.register_video_generator(MoneyPrinterTurboProvider(mpt_dir))
    
    reality = CapabilityRegistry()
    genome_lib = GenomeLibrary(db_path="prod_genome.jsonl")
    reality.register_research_provider(StochasticResearchProvider(genome_lib))
    
    start = time.time()
    try:
        videos = 0
        max_cycles = 1 if os.environ.get("TEST_MODE") == "true" else 288
        while videos < max_cycles and (time.time() - start < 24 * 3600): # 24 horas
            runner = ExperimentRunner(
                db=db, registry=hypo, reality_registry=reality, 
                factory_registry=factory, profile=profile
            )
            runner.is_synthetic = True
            print(f"\n--- Iniciando ciclo de burn-in #{videos+1} ---")
            runner.run_cycle(stop_at_state=ExperimentState.ASSET_GENERATED)
            videos += 1
            if videos < max_cycles:
                print("Aguardando 5 minutos de cooldown térmico/RAM...")
                time.sleep(300) 
    except KeyboardInterrupt:
        print("\nBurn-In abortado manualmente.")
        
    print(f"Burn-In finalizado. Vídeos gerados: {videos}")

if __name__ == "__main__":
    burn_in()
