import sys
import os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.revenue_os.analytics.research_registry import ResearchLedger
from src.reality.base import CapabilityRegistry
from src.factory.base import FactoryRegistry
from src.services.experiment_runner import ExperimentRunner, ExperimentState

from src.factory.video.moneyprinterturbo.adapter import MoneyPrinterTurboProvider
from src.factory.image.nvidia.provider import NvidiaImageProvider
from src.reality.research.stochastic_provider import StochasticResearchProvider
from src.reality.social.pinterest.browser import PinterestBrowserProvider
from src.revenue_os.analytics.genome_library import GenomeLibrary
# from src.integrations.pinterest.provider import PinterestProvider

def run_canary():
    print("===========================================")
    print(" [AI Revenue OS] CANARY RELEASE (EXP-001B.0) ")
    print("===========================================")
    
    db_path = "prod_db.sqlite3"
    db = ExperimentDatabase(db_path)
    hypo = HypothesisRegistry(db)
    ledger = ResearchLedger(db)
    genome_lib = GenomeLibrary(db_path="prod_genome.jsonl")
    
    factory = FactoryRegistry()
    mpt_dir = Path(__file__).parent.parent / "MoneyPrinterTurbo"
    factory.register_video_generator(MoneyPrinterTurboProvider(mpt_dir))
    factory.register_image_generator(NvidiaImageProvider())
    
    reality = CapabilityRegistry()
    reality.register_research_provider(StochasticResearchProvider(genome_lib))
    reality.register_publisher(PinterestBrowserProvider())
    
    max_posts = 3
    for i in range(1, max_posts + 1):
        print(f"\n--- Gerando Canary Post {i}/{max_posts} ---")
        try:
            runner = ExperimentRunner(
                db=db,
                registry=hypo,
                reality_registry=reality,
                factory_registry=factory,
                research_ledger=ledger,
                require_human_approval=True
            )
            runner.is_synthetic = False 
            result = runner.run_cycle(stop_at_state=ExperimentState.HUMAN_APPROVED)
            if result.get("status") == "success" or "Awaiting human approval" in str(result.get("error", "")):
                print(f"✅ Canary gerado com sucesso.")
                print(f"📁 Arquivos em: experiments/{runner.ctx.get('experiment_id')}")
            else:
                print(f"❌ Erro no Canary {i}: {result.get('error')}")
        except Exception as e:
            print(f"❌ Erro fatal inesperado no Canary {i}: {e}")
                
if __name__ == "__main__":
    run_canary()
