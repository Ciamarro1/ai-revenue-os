import sys
import os
from pathlib import Path
import random
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.revenue_os.analytics.genome_library import GenomeLibrary
from src.reality.social.synthetic_metrics import SyntheticMetricsProvider

def run_synthetic_replay():
    print("[EXP-001A.6] Iniciando Synthetic Market Replay (Adversarial Regime Change)")
    
    # Limpa a biblioteca para garantir inicio zerado
    db_path = "test_synthetic_genome.jsonl"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    genome_lib = GenomeLibrary(db_path)
    metrics_provider = SyntheticMetricsProvider(hidden_regime="A")
    
    possible_hooks = ["contrarian", "educational", "storytelling", "listicle"]
    possible_emotions = ["curiosity", "trust", "fear", "joy"]
    
    def simulate_loops(start, end, label):
        print(f"\n--- {label} ({start} a {end}) ---")
        for i in range(start, end + 1):
            hook = random.choice(possible_hooks)
            emotion = random.choice(possible_emotions)
            
            attributes = {
                "hook": {"type": hook},
                "psychology": {"emotion": emotion}
            }
            genome_id = f"{hook}_{emotion}"
            
            metrics = metrics_provider.evaluate_genome(attributes)
            # Reward arbitrario normalizado: CTR (0-20%) -> (0-1.0)
            reward = min(1.0, (metrics.outbound_clicks / max(1, metrics.impressions)) * 5)
            
            genome_lib.extract_and_catalog(genome_id, attributes, reward)
            
        best = genome_lib.get_best_genomes(top_n=3)
        print("Melhores genomas percebidos pela Library:")
        for b in best:
            print(f"- {b['genome_id']}: Exp. Reward: {b['expected_reward']:.3f} | Confidence: {b['confidence']:.2f} | N: {b['sample_size']}")

    # Fase 1: Regime A (contrarian + curiosity)
    print("Vencedor Oculto Injetado: contrarian + curiosity")
    simulate_loops(1, 100, "Fase 1: Noisy Environment")
    
    # Fase 2: Regime Change (educational + trust)
    print("\n[MERCADO MUDOU] O Vencedor Oculto agora é: educational + trust")
    metrics_provider.hidden_regime = "B"
    # Damos 200 iteracoes para que a library perceba a queda do antigo vencedor 
    # e ascensao do novo (média móvel precisa diluir o passado)
    simulate_loops(101, 300, "Fase 2: Adversarial Regime Change")
    
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    run_synthetic_replay()
