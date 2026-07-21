import random
from typing import Dict, Any, List
from src.reality.base import ResearchProvider
from src.reality.research.schemas import ResearchReport

class StochasticResearchProvider(ResearchProvider):
    """
    Gera genomas aleatoriamente para o torneio cego, sem buscar dados externos.
    Se a diversidade da biblioteca cair muito (convergência prematura), força
    novas mutações aleatórias.
    """
    def __init__(self, genome_library=None):
        self.provider_name = "stochastic_mutator"
        self.confidence_score = 1.0
        self.genome_library = genome_library
        
        self.hooks = ["curiosity", "contrarian", "authority", "urgency", "surprise"]
        self.emotions = ["fear", "aspiration", "belonging", "status", "discovery"]
        self.structures = ["listicle", "story", "tutorial", "comparison", "reveal"]
        self.audiences = ["beginner", "expert", "buyer", "creator"]
        self.visuals = ["cinematic", "minimal", "documentary", "fast-cut", "infographic"]

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "provider": self.provider_name}

    def _generate_random_genome(self) -> Dict[str, Any]:
        return {
            "hook": {"type": random.choice(self.hooks), "strength": 0.5},
            "psychology": {"emotion": random.choice(self.emotions), "pain_point": "unknown"},
            "structure": {"format": random.choice(self.structures), "duration": 30, "tempo": "fast"},
            "audience": {"persona": random.choice(self.audiences)},
            "visual_language": {"style": random.choice(self.visuals), "palette": "dark"}
        }
        
    def _mutate_winner(self, winner: Dict[str, Any]) -> Dict[str, Any]:
        mutant = dict(winner["attributes"])
        aspect = random.choice(["hook", "psychology", "structure", "audience", "visual_language"])
        if aspect == "hook": mutant["hook"]["type"] = random.choice(self.hooks)
        elif aspect == "psychology": mutant["psychology"]["emotion"] = random.choice(self.emotions)
        elif aspect == "structure": mutant["structure"]["format"] = random.choice(self.structures)
        elif aspect == "audience": mutant["audience"]["persona"] = random.choice(self.audiences)
        elif aspect == "visual_language": mutant["visual_language"]["style"] = random.choice(self.visuals)
        return mutant

    def execute_research(self, query: str, context: Dict[str, Any] = None) -> ResearchReport:
        genome_candidate = self._generate_random_genome()
        
        if self.genome_library:
            diversity = self.genome_library.measure_diversity()
            if diversity < 0.40:
                print(f"🧬 [Mutação Forçada] Diversidade crítica ({diversity}). Injetando sangue novo.")
            else:
                winners = self.genome_library.get_best_genomes(top_n=3)
                if winners and random.random() > 0.5:
                    winner = random.choice(winners)
                    genome_candidate = self._mutate_winner(winner)
                    print(f"🧬 [Cruzamento] Mutando campeão: {winner['genome_id']}")

        topic = "AI Tools"
        hook_text = genome_candidate["hook"]["type"]
        
        return ResearchReport(
            query="stochastic exploration",
            provider=self.provider_name,
            sources=["internal_rng"],
            trends=[{
                "topic": topic, 
                "category": "blind_test", 
                "suggested_hook": hook_text,
                "genome_candidate": genome_candidate
            }],
            competitors=[],
            keywords=[]
        )
