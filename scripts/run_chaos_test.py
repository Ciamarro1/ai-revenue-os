import sys, random, time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.services.experiment_runner import ExperimentRunner, ExperimentState
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.revenue_os.analytics.profile import ExperimentProfile
from src.factory.base import FactoryRegistry
from src.reality.base import CapabilityRegistry
from src.factory.schemas import CreativeBrief, GeneratedAsset
from src.reality.research.schemas import ResearchReport

class ChaosFactoryProvider:
    provider_name = "chaos"
    confidence_score = 0.9
    def generate(self, brief: CreativeBrief) -> GeneratedAsset:
        r = random.random()
        if r < 0.2:
            raise RuntimeError("Chaos: Disco cheio durante renderização")
        elif r < 0.4:
            raise RuntimeError("Chaos: Processo morreu com código de saída 137 (OOM)")
        elif r < 0.6:
            raise RuntimeError("Chaos: JSON de resposta corrompido")
        elif r < 0.7:
            raise RuntimeError("Chaos: Timeout no SQLite Locked")
        return GeneratedAsset(path="mock.mp4", duration=10, resolution="1080x1920", provider="chaos", confidence=0.9)

class MockResearch:
    provider_name = "mock"
    confidence_score = 0.9
    def execute_research(self, query, context=None):
        if random.random() < 0.3: 
            raise RuntimeError("Chaos: Timeout na API de pesquisa (HTTP 429 Too Many Requests)")
        return ResearchReport(query=query, provider="mock", trends=[{"topic": "chaos", "category": "test"}])

def chaos_test():
    print("===========================================")
    print(" [AI Revenue OS] CHAOS ENGINEERING TEST    ")
    print("===========================================")
    
    db = ExperimentDatabase("prod_db.sqlite3")
    hypo = HypothesisRegistry(db)
    profile = ExperimentProfile("config/experiment_profile.yaml")
    
    factory = FactoryRegistry()
    factory.register_video_generator(ChaosFactoryProvider())
    reality = CapabilityRegistry()
    reality.register_research_provider(MockResearch())

    for i in range(5):
        print(f"\n--- Injetando Caos #{i+1} ---")
        runner = ExperimentRunner(db=db, registry=hypo, reality_registry=reality, factory_registry=factory, profile=profile)
        runner.is_synthetic = True
        res = runner.run_cycle(stop_at_state=ExperimentState.PUBLISHED)
        
        if res.get("status") == "failed":
            print(f"🛡️ Resiliência ativada: Sistema logou falha '{res.get('error')}' no evento sem corromper estado.")

if __name__ == "__main__":
    chaos_test()
