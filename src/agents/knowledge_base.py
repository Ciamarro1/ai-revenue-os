import json
from pathlib import Path
from typing import Dict, Any, List

class CreativeKnowledgeBase:
    """
    Base de conhecimento persistente (EXP-006).
    Acumula aprendizados do CreativeOptimizer sobre padrões que geram
    baixa retenção, falta de dinamismo, ou rejeição.
    Alimenta o CreativePlanner para evitar repetição de erros crônicos.
    """
    def __init__(self, storage_dir: str = "knowledge"):
        self.db_path = Path(__file__).parent.parent.parent / storage_dir / "patterns.json"
        self._ensure_db()
        
    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({"patterns": []}, f, indent=2)
                
    def load_patterns(self) -> List[Dict[str, Any]]:
        with open(self.db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("patterns", [])
            
    def register_learning(self, pattern: str, severity: str, average_score_loss: int = 10):
        """Registra um padrão negativo descoberto pelo Optimizer."""
        patterns = self.load_patterns()
        
        # Se o padrão já existe, incrementa a frequência
        existing = next((p for p in patterns if p["pattern"] == pattern), None)
        if existing:
            existing["frequency"] += 1
            # Recalcula média (simplificada para o exemplo)
            existing["average_score_loss"] = (existing["average_score_loss"] + average_score_loss) // 2
        else:
            patterns.append({
                "pattern": pattern,
                "severity": severity,
                "frequency": 1,
                "average_score_loss": average_score_loss
            })
            
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump({"patterns": patterns}, f, indent=2, ensure_ascii=False)
            
        print(f"🧠 [KnowledgeBase] Novo padrão de falha registrado: '{pattern}' (Frequência: {existing['frequency'] if existing else 1})")
