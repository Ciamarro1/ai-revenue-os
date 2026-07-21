import logging
import time
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.genome_library import GenomeLibrary
from src.services.calibration.metrics_provider import RealityMetricsProvider
from src.services.calibration.reward_calculator import EconomicsRewardCalculator

logger = logging.getLogger(__name__)

class CalibrationService:
    """
    Worker assíncrono independente. 
    Busca o mundo real e injeta as consequências das ações autônomas 
    de volta na base de conhecimento (Bayesian Update / Evolution).
    """
    def __init__(self, db: ExperimentDatabase, genome_library: GenomeLibrary):
        self.db = db
        self.genome_library = genome_library
        self.metrics_provider = RealityMetricsProvider()
        self.calculator = EconomicsRewardCalculator()
        
    def has_urgent_pending(self) -> bool:
        return False # A ser feito de outra forma
        
    def process_pending_experiments(self, worker_id: str = "worker-1"):
        experiments = self.db.lock_experiments_for_calibration(worker_id)
        if not experiments:
            return
            
        print(f"[CalibrationService] {len(experiments)} experimentos engatados (Status: CALIBRATING por {worker_id})")
        
        for exp in experiments:
            try:
                # 1. Fetch
                metrics = self.metrics_provider.fetch(exp)
                
                # 2. Calculate Real Economics
                reward = self.calculator.calculate(metrics, exp.economics.generation_cost_usd)
                
                # 3. Update Genome Knowledge
                # O Genome ID real é guardado num mapa ou no file_hash/creative_hash. 
                # Estamos associando com o hash do criativo para o laboratório evolutivo
                genome_id = exp.creative_hash 
                self.genome_library.extract_and_catalog(
                    genome_id=genome_id,
                    attributes={}, # O genoma já existe na library se usou replay, senão isso o cria vazio. O ideal é resgatar o genoma completo.
                    reward=reward,
                    is_real_world=True
                )
                
                # 4. Mark Calibrated
                exp.real_world_metrics = metrics
                exp.reward_score = reward
                exp.status = "CALIBRATED"
                self.db.insert_experiment(exp)
                
                print(f"✅ [{exp.experiment_id}] Calibrado. CTR Real: {metrics.ctr_percent:.2f}% | Lucro: ${metrics.profit_usd:.2f} | Recompensa Final: {reward:.3f}")
            except Exception as e:
                print(f"❌ Falha ao calibrar {exp.experiment_id}: {e}")
