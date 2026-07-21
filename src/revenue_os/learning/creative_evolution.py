import random
from typing import Dict, Any, List

class CreativeEvolution:
    """
    Motor de Evolução Criativa (Creative Crossover & Mutation).
    Combina os ganchos e termos de maior sucesso para criar a próxima iteração criativa mutada.
    """
    @staticmethod
    def evolve_hypothesis(winning_patterns: Dict[str, Any], base_topic: str) -> Dict[str, Any]:
        words = winning_patterns.get("winning_key_words", [])
        categories = winning_patterns.get("top_categories", ["finance"])

        # Ganchos de Crossover pré-estruturados que performam bem
        crossover_hooks = [
            "O segredo que ninguém te conta sobre {topic}.",
            "Como {word} revolucionou minha visão de {topic}.",
            "Pare de cometer esse erro com {topic} se você quer {word}.",
            "A verdade sobre {topic} revelada por especialistas."
        ]

        # Mutação: escolhe um padrão e insere termos bem-sucedidos
        hook_template = random.choice(crossover_hooks)
        word = words[0] if words else "lucro"
        
        evolved_statement = hook_template.format(topic=base_topic, word=word)
        chosen_category = random.choice(categories) if categories else "finance"

        return {
            "statement": evolved_statement,
            "category": chosen_category,
            "metric_target": "ctr_percent"
        }
