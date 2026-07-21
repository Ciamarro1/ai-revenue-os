import time
from typing import List, Dict, Any

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False

class SocialSafetyGate:
    """
    Guardião anti-spam Híbrido (EXP-001A.7)
    Protege o laboratório contra punições da rede social.
    Usa um modelo composto:
    35% embedding similarity
    20% lexical similarity (Jaccard)
    20% temporal behavior (Cooldown)
    15% asset hash
    10% publishing pattern (Mocked)
    """
    def __init__(self, db_history: List[Dict[str, Any]] = None, use_embeddings: bool = True):
        self.history = db_history or []
        self.cooldown_seconds = 3600
        
        self.use_embeddings = use_embeddings and HAS_EMBEDDINGS
        if self.use_embeddings:
            # Modelo leve e rápido que roda na CPU sem problemas
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.model = None
            print("[Warning] SentenceTransformers não está disponível. Usando fallback Lexical puro.")
        
    def _lexical_similarity(self, text1: str, text2: str) -> float:
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0
        
    def _embedding_similarity(self, text1: str, text2: str) -> float:
        if not self.use_embeddings:
            return self._lexical_similarity(text1, text2) # fallback 
            
        emb1 = self.model.encode(text1)
        emb2 = self.model.encode(text2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        if norm1 == 0 or norm2 == 0: return 0.0
        sim = np.dot(emb1, emb2) / (norm1 * norm2)
        return max(0.0, float(sim))

    def _temporal_risk(self, current_time: float, past_time: float) -> float:
        # Se postou há menos de 10 min (600s), risco = 1.0
        # Decai linearmente até 1 hora (3600s)
        diff = current_time - past_time
        if diff < 600:
            return 1.0
        if diff >= self.cooldown_seconds:
            return 0.0
        return 1.0 - ((diff - 600) / (self.cooldown_seconds - 600))
        
    def check_safety(self, title: str, description: str, file_hash: str) -> Dict[str, Any]:
        current_time = time.time()
        
        max_risk = 0.0
        max_reason = "OK"
        
        for past_post in self.history:
            past_title = past_post.get("title", "")
            
            # Scores Individuais
            emb_sim = self._embedding_similarity(title, past_title)
            lex_sim = self._lexical_similarity(title, past_title)
            temp_risk = self._temporal_risk(current_time, past_post.get("timestamp", 0))
            
            hash_risk = 1.0 if (file_hash and past_post.get("hash") == file_hash) else 0.0
            pub_pattern_risk = 0.2 # Valor mock para comportamento repetitivo 
            
            # SocialRiskScore Composto
            social_risk = (0.35 * emb_sim) + (0.20 * lex_sim) + (0.20 * temp_risk) + (0.15 * hash_risk) + (0.10 * pub_pattern_risk)
            
            if social_risk > max_risk:
                max_risk = social_risk
                reasons = []
                if emb_sim > 0.8: reasons.append(f"Alta Similaridade Semântica ({emb_sim:.2f})")
                if lex_sim > 0.8: reasons.append("Repetição Lexical Exata")
                if temp_risk > 0.8: reasons.append("Cooldown Ativo")
                if hash_risk == 1.0: reasons.append("Mídia Duplicada")
                max_reason = " | ".join(reasons) if reasons else "Risco Híbrido Acumulado"
                
        if max_risk > 0.70:
            return {"safe": False, "reason": "SOCIAL_RISK_HIGH", "details": max_reason, "score": round(max_risk, 3)}
            
        return {"safe": True, "reason": "OK", "score": round(max_risk, 3)}
