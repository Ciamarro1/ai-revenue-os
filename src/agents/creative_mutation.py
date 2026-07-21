from typing import List, Dict, Any
import uuid

from src.revenue_os.analytics.schemas import CreativeGenome

class CreativeMutationAgent:
    """
    O Geneticista Criativo.
    Não tenta "melhorar" um roteiro (papel do Optimizer).
    Em vez disso, ele pega o DNA (Creative Genome) de um vídeo vencedor e realiza
    MUTAÇÕES controladas para explorar o espaço de soluções sem saturar a audiência.
    """
    def __init__(self, llm_provider=None):
        self.llm = llm_provider

    def generate_mutations(self, winner_genome: CreativeGenome, n_mutations: int = 5) -> List[CreativeGenome]:
        """
        Recebe um genoma validado pelo DecisionEngine (SCALE ou ITERATE) e
        deriva novas linhagens mantendo o core-causal, mas iterando o exterior.
        """
        mutations = []
        
        # Em produção, o LLM receberia o winner_genome em formato JSON e o seguinte prompt:
        # "Mantenha a 'estrutura' e a 'audiência' intactas, mas alterne a 'emoção' (semantic) 
        # e o 'estilo' (visual). Crie {n_mutations} variantes."
        
        # Mock do comportamento mutacional determinístico:
        for i in range(n_mutations):
            # Mutação A: Mantém narrativa, altera a emoção superficial
            new_semantic = winner_genome.semantic.copy()
            if i % 2 == 0:
                new_semantic["emotion"] = "urgency" if winner_genome.semantic.get("emotion") == "curiosity" else "curiosity"
                new_semantic["novelty"] = min(1.0, new_semantic.get("novelty", 0) + 0.1)
                
            # Mutação B: Mantém a emoção, altera o visual
            new_visual = winner_genome.visual.copy()
            if i % 3 == 0:
                new_visual["pace"] = "hyper-fast" if winner_genome.visual.get("pace") == "fast" else "fast"
                
            mutated_genome = CreativeGenome(
                genome_id=f"MUT-{uuid.uuid4().hex[:6].upper()}",
                semantic=new_semantic,
                structure=winner_genome.structure.copy(), # O core vencedor é protegido
                visual=new_visual,
                audience=winner_genome.audience.copy()
            )
            mutations.append(mutated_genome)
            
        return mutations
