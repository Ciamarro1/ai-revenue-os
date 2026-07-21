import json
import os
import math
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class Genome(BaseModel):
    """
    Especificação formal de um Genoma Criativo (Sprint 7.4).
    Mapeia variáveis criativas e comportamentais para cálculo do Genome Score.
    """
    id: Optional[str] = None
    hook: str
    emotion: str
    visual_style: str
    colors: List[str] = Field(default_factory=list)
    cta: str
    length: int = 15
    music: str = "ambient"
    narration: str = "ai_voice"
    platform: str = "pinterest"
    audience: str = "general"
    topic: str = "lifestyle"
    offer: str = "none"
    keywords: List[str] = Field(default_factory=list)
    thumbnail: str = "default.png"
    posting_time: str = "18:00"
    format: str = "pin_video"
    
    # Métricas empíricas de performance
    ctr: float = 0.0
    save_rate: float = 0.0
    conversion_rate: float = 0.0
    revenue: float = 0.0
    observations_count: int = 0

    @property
    def score(self) -> float:
        """
        Calcula o Genome Score ponderando CTR, Save Rate, Conversão e Receita.
        """
        return self.adaptive_score(total_system_samples=self.observations_count)

    def get_adaptive_weights(self, total_system_samples: int = 0) -> Dict[str, float]:
        """
        Adapta dinamicamente os pesos de pontuação com base no tamanho da amostra acumulada do sistema.
        À medida que o volume de dados aumenta, o peso da receita financeira aumenta gradativamente.
        """
        sample_count = max(self.observations_count, total_system_samples)
        if sample_count < 10:
            return {"ctr": 0.35, "save_rate": 0.25, "conversion": 0.25, "revenue": 0.15}
        
        # Rebalanceamento dinâmico adaptativo dos pesos ex-post
        rev_weight = min(0.50, 0.15 + (math.log10(max(10, sample_count)) - 1.0) * 0.10)
        rem = 1.0 - rev_weight
        return {
            "ctr": round(rem * 0.40, 3),
            "save_rate": round(rem * 0.30, 3),
            "conversion": round(rem * 0.30, 3),
            "revenue": round(rev_weight, 3)
        }

    def adaptive_score(self, total_system_samples: int = 0) -> float:
        w = self.get_adaptive_weights(total_system_samples)
        obs_weight = math.log10(self.observations_count + 1) if self.observations_count > 0 else 0.5
        base_score = (self.ctr * w["ctr"]) + (self.save_rate * w["save_rate"]) + (self.conversion_rate * w["conversion"]) + (min(self.revenue, 100.0) / 100.0 * w["revenue"])
        return round(base_score * obs_weight * 100.0, 2)


class GenomeLibrary:
    """
    O Knowledge Layer Evolutivo (Genome V2).
    Aprende padrões sob incerteza medindo taxa de vitória, 
    recompensa esperada e confiança estatística do genoma.
    Agora inclui Variância e Robustez (EXP-001A.7).
    """
    def __init__(self, db_path: str = "genome_library.jsonl"):
        self.db_path = db_path
        self.catalog = self._load()
        
    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.db_path):
            return {}
        catalog = {}
        with open(self.db_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                catalog[record["genome_id"]] = record
        return catalog
        
    def _calc_confidence(self, sample_size: int, success_rate: float, variance: float) -> float:
        if sample_size == 0:
            return 0.0
        volume = min(1.0, math.log10(max(1, sample_size)) / 2.0)
        stability_penalty = min(0.5, variance) 
        return round(max(0.0, volume - stability_penalty), 3)

    def extract_and_catalog(self, genome_id: str, attributes: Dict[str, Any], reward: float, is_real_world: bool = False):
        is_success = reward >= 0.50 
        
        if genome_id not in self.catalog:
            self.catalog[genome_id] = {
                "genome_id": genome_id,
                "version": 1,
                "parent_a": attributes.pop("_parent_a", None),
                "parent_b": attributes.pop("_parent_b", None),
                "created_at": datetime.now(timezone.utc).isoformat() + "Z",
                "source": "production" if is_real_world else "synthetic",
                "attributes": attributes,
                "sample_size": 0,
                "real_world_samples": 0,
                "wins": 0,
                "losses": 0,
                "expected_reward": 0.0,
                "variance": 0.0,
                "success_rate": 0.0,
                "confidence": 0.0,
                "robustness": 0.0,
                "generation": 1
            }
            
        entry = self.catalog[genome_id]
        n = entry["sample_size"]
        old_mean = entry["expected_reward"]
        
        entry["sample_size"] += 1
        if is_real_world:
            entry.setdefault("real_world_samples", 0)
            entry["real_world_samples"] += 1
            
        if is_success:
            entry["wins"] += 1
        else:
            entry["losses"] += 1
            
        # Atualização online da Média
        new_mean = old_mean + (reward - old_mean) / entry["sample_size"]
        entry["expected_reward"] = round(new_mean, 4)
        
        # Atualização online da Variância (Aproximada Welford)
        if entry["sample_size"] > 1:
            old_variance = entry["variance"]
            entry["variance"] = round((old_variance * (n - 1) + (reward - old_mean)*(reward - new_mean)) / n, 4)
        
        entry["success_rate"] = round(entry["wins"] / entry["sample_size"], 4)
        entry["confidence"] = self._calc_confidence(entry["sample_size"], entry["success_rate"], entry["variance"])
        
        # Robustez penaliza genomas com alta variância
        entry["robustness"] = round((entry["expected_reward"] * entry["confidence"]) / (1.0 + entry["variance"]), 4)
        
        self._persist()
        
    def _persist(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            for entry in self.catalog.values():
                f.write(json.dumps(entry) + "\n")

    def measure_diversity(self) -> float:
        """
        Mede a diversidade da população (Simpson's Diversity Index).
        Previne convergência prematura.
        """
        if not self.catalog:
            return 1.0
        hooks_count = {}
        total = 0
        for entry in self.catalog.values():
            if entry["sample_size"] > 0:
                h = entry["attributes"].get("hook", {}).get("type", "unknown")
                hooks_count[h] = hooks_count.get(h, 0) + 1
                total += 1
        if total == 0:
            return 1.0
            
        sum_sq = sum((count/total)**2 for count in hooks_count.values())
        return round(1.0 - sum_sq, 3)
                
    def get_best_genomes(self, top_n: int = 3, require_production_readiness: bool = False) -> List[Dict[str, Any]]:
        valid = []
        for g in self.catalog.values():
            if require_production_readiness:
                if (g["sample_size"] >= 30 and 
                    g.get("real_world_samples", 0) >= 10 and 
                    g["confidence"] >= 0.75 and 
                    g["robustness"] > 0):
                    valid.append(g)
            else:
                if g["confidence"] >= 0.2:
                    valid.append(g)
                    
        if not valid and not require_production_readiness:
            return sorted(self.catalog.values(), key=lambda x: x["expected_reward"], reverse=True)[:top_n]
        
        valid.sort(key=lambda x: x["robustness"], reverse=True)
        return valid[:top_n]
