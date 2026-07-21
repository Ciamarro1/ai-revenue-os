import sys
import os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.revenue_os.analytics.genome_library import GenomeLibrary
from src.reality.base import CapabilityRegistry, Publisher
from src.factory.base import FactoryRegistry, VideoGenerator
from src.factory.schemas import GeneratedAsset
from src.reality.research.stochastic_provider import StochasticResearchProvider
from src.reality.social.synthetic_metrics import SyntheticMetricsProvider
from src.services.experiment_runner import ExperimentRunner, ExperimentState
from src.reality.base import PublishedContent, CanonicalMetrics
import unittest.mock

class FastMockFactory(VideoGenerator):
    def __init__(self):
        self.provider_name = "fast_mock_factory"
        self.confidence_score = 1.0
    def health(self) -> dict: return {"status": "ok"}
    def generate(self, brief):
        return GeneratedAsset(path="mock.mp4", duration=brief.duration, resolution="1080p", provider=self.provider_name, confidence=1.0)

class FastMockPublisher(Publisher):
    def __init__(self):
        self.provider_name = "fast_mock_publisher"
        self.confidence_score = 1.0
    def health(self) -> dict: return {"status": "ok"}
    def publish_image(self, *args, **kwargs):
        return PublishedContent(content_id=f"pub_{id(self)}", platform="mock", status="published", url="mock")
    def publish_video(self, *args, **kwargs): return self.publish_image()
    def archive_content(self, *args, **kwargs): return True

def run_tournament():
    print("[EXP-001A.7] Iniciando Blind Genome Tournament (Evolução Cega)")
    
    # Configura Banco e Library
    db_path_sql = "test_tournament_db.sqlite3"
    if os.path.exists(db_path_sql): os.remove(db_path_sql)
    db = ExperimentDatabase(db_path_sql) 
    hypo = HypothesisRegistry(db)
    db_path = "test_tournament.jsonl"
    if os.path.exists(db_path): os.remove(db_path)
    
    genome_lib = GenomeLibrary(db_path)
    
    reality = CapabilityRegistry()
    reality.register_research_provider(StochasticResearchProvider(genome_lib))
    reality.register_publisher(FastMockPublisher())
    
    # Synthetic Simulator onde "contrarian" + "curiosity" ganha
    metrics = SyntheticMetricsProvider(hidden_regime="A")
    reality.register_metrics_provider(metrics)
    
    factory = FactoryRegistry()
    factory.register_video_generator(FastMockFactory())
    
    # Pula checagem de politica econômica e física pra simulação rodar a 1000/s
    with unittest.mock.patch('src.services.experiment_runner.VideoQualityGate.check_quality', return_value=True), \
         unittest.mock.patch('src.revenue_os.analytics.policy.PolicyEngine.check_can_publish', return_value={"allowed": True, "reason": "ok"}):
         
        runner = ExperimentRunner(db=db, registry=hypo, reality_registry=reality, factory_registry=factory)
        
        print("\n--- Iniciando Evolução de 100 Ciclos ---")
        for i in range(1, 101):
            runner.ctx = {}
            runner.run_cycle() # Vai ate CALIBRATED
            
            # Catalogação do Genoma após fechamento do ciclo (já que ainda n acoplamos hard-coded no ExperimentRunner)
            genome = runner.ctx["genome"]
            reward = runner.ctx["experiment_contract"].reward_score
            genome_id = f"{genome.hook['type']}_{genome.psychology['emotion']}"
            
            # Normalizamos o reward apenas para o catálogo para manter robustez em testes estocásticos
            normalized_reward = min(1.0, reward / 10.0)
            genome_lib.extract_and_catalog(genome_id, genome.model_dump(), normalized_reward)
            
            if i % 25 == 0:
                print(f"[{i}/100] Diversidade Atual da População (Simpson Index): {genome_lib.measure_diversity():.2f}")
                
    print("\n--- FIM DO TORNEIO EVOLUTIVO ---")
    print("Sobreviventes (Top 5 Genomas Evoluídos):")
    top5 = genome_lib.get_best_genomes(top_n=5)
    for idx, t in enumerate(top5):
        print(f"{idx+1}. Genoma: {t['genome_id']} | Confiança: {t['confidence']} | Robustez: {t['robustness']} | Reward Estimado: {t['expected_reward']} | Testes: {t['sample_size']}")

if __name__ == "__main__":
    run_tournament()
