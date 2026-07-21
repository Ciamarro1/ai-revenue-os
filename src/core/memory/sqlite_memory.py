import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.core.memory.interface import MemoryProvider

class SQLiteMemoryProvider(MemoryProvider):
    """
    Provedor de memória episódica/semântica persistido em SQLite.
    Usa similaridade Jaccard de tokens local para buscas textuais e
    retrieval contextual rápido sem requisições de rede.
    """
    def __init__(self, db: Any):
        self.db = db

    def _get_conn(self):
        return self.db._get_conn()

    def store(self, content: str, memory_type: str, metadata: Dict[str, Any]) -> str:
        """Salva uma memória episódica ou factual na tabela semantic_memories."""
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        metadata_str = json.dumps(metadata)
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO semantic_memories (memory_type, content, metadata_json, created_at)
                VALUES (?, ?, ?, ?)
            """, (memory_type, content, metadata_str, ts))
            row_id = c.lastrowid
            conn.commit()
        return str(row_id)

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Realiza busca por palavras-chave cruzando interseções de termos."""
        query_words = set(query.strip().lower().split())
        if not query_words:
            return []
            
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, memory_type, content, metadata_json, created_at FROM semantic_memories")
            rows = c.fetchall()
            
        results = []
        for r in rows:
            content_text = r[2]
            content_words = set(content_text.strip().lower().split())
            
            # Jaccard index similarity
            intersection = query_words.intersection(content_words)
            union = query_words.union(content_words)
            score = len(intersection) / len(union) if union else 0.0
            
            if score > 0.0:
                results.append({
                    "id": str(r[0]),
                    "memory_type": r[1],
                    "content": content_text,
                    "metadata": json.loads(r[3]),
                    "created_at": r[4],
                    "score": score
                })
                
        # Ordena descendente por score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def retrieve_context(self, entity: str, limit: int = 3) -> str:
        """Formata as memórias recuperadas para injeção no prompt do agente."""
        memories = self.search(entity, limit=limit)
        if not memories:
            return "Nenhuma experiência episódica ou aprendizado anterior relevante recuperado."
            
        blocks = []
        for idx, m in enumerate(memories, 1):
            meta_str = ", ".join(f"{k}: {v}" for k, v in m["metadata"].items())
            blocks.append(f"[{idx}] {m['content']} (Tipo: {m['memory_type']}, Metadados: {{{meta_str}}})")
            
        return "\n".join(blocks)

