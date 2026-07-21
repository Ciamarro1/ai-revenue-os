from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.learning.success_memory import SuccessMemory
from src.revenue_os.learning.failure_memory import FailureMemory
from src.revenue_os.learning.pattern_extractor import PatternExtractor
from src.revenue_os.learning.creative_evolution import CreativeEvolution

class StrategyEngine:
    """
    Orquestrador do Loop de Aprendizado Adaptativo (Strategy Engine).
    Lê o histórico operacional do laboratório, extrai aprendizados baseados em evidência
    e injeta uma nova hipótese evolucionária no banco operacional para fechar o ciclo.
    """
    def __init__(self, db: ExperimentDatabase):
        self.db = db
        self.success_mem = SuccessMemory(db)
        self.fail_mem = FailureMemory(db)

    def run_learning_cycle(self, base_topic: str) -> dict:
        print("🧠 [StrategyEngine] Iniciando Ciclo de Aprendizado Adaptativo...")
        
        # 1. Recuperar dados empíricos históricos do banco operacional
        successes = self.success_mem.get_success_genomes()
        failures = self.fail_mem.get_failed_genomes()
        
        print(f"  => Histórico carregado: {len(successes)} sucessos, {len(failures)} falhas.")
        
        # 2. Extrair os padrões e termos vencedores de maior peso estatístico
        patterns = PatternExtractor.extract_patterns(successes, failures)
        
        # 3. Evoluir o genoma criativo cruzando dados passados
        evolved = CreativeEvolution.evolve_hypothesis(patterns, base_topic)
        print(f"  => Genoma Criativo Evoluído: '{evolved['statement']}' (Categoria: {evolved['category']})")
        
        # 4. Injetar no banco operacional hypotheses
        conn = self.db._get_conn()
        try:
            c = conn.cursor()
            c.execute(
                "INSERT INTO hypotheses (statement, metric_target, category, status) VALUES (?, ?, ?, 'testing')",
                (evolved["statement"], evolved["metric_target"], evolved["category"])
            )
            conn.commit()
            print("✅ [StrategyEngine] Ciclo completo! Nova hipótese evolutiva injetada na base.")
        finally:
            if conn and self.db.db_file != ":memory:":
                conn.close()
                
        return evolved
