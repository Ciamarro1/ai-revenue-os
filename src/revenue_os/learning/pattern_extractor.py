from typing import List, Dict, Any

class PatternExtractor:
    """
    Extrator de Padrões Criativos.
    Analisa os genomas de sucesso e falha históricas para extrair palavras-chave,
    tópicos ou categorias que se correlacionam positivamente com alta performance.
    """
    @staticmethod
    def extract_patterns(successes: List[Dict[str, Any]], failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        winning_categories = {}
        losing_categories = {}
        winning_hooks = []
        
        for item in successes:
            cat = item.get("category")
            if cat:
                winning_categories[cat] = winning_categories.get(cat, 0) + 1
            
            stmt = item.get("statement", "")
            # Coleta termos importantes dos hooks vencedores (ignora conectivos pequenos)
            for word in stmt.lower().replace(",", "").replace(".", "").split():
                if len(word) > 4 and word not in winning_hooks:
                    winning_hooks.append(word)

        for item in failures:
            cat = item.get("category")
            if cat:
                losing_categories[cat] = losing_categories.get(cat, 0) + 1

        # Filtra categorias que ganham mas não perdem
        strong_categories = []
        for cat, win_count in winning_categories.items():
            lose_count = losing_categories.get(cat, 0)
            if win_count > lose_count:
                strong_categories.append(cat)

        return {
            "top_categories": strong_categories or ["finance", "productivity"],
            "winning_key_words": winning_hooks[:10]
        }
