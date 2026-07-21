import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
from src.revenue_os.analytics.database import ExperimentDatabase

logger = logging.getLogger("revenue_os.knowledge_graph")


class KnowledgeGraph:
    """
    Relações semânticas entre conceitos e nichos no AI Revenue OS.
    Permite à inteligência de pesquisa relacionar tópicos (ex: "home office" -> "notebook" -> "chatgpt").
    """
    def __init__(self, db: ExperimentDatabase):
        self.db = db

    def add_relation(self, source_concept: str, target_concept: str, weight: float = 1.0):
        """Adiciona ou atualiza o peso da aresta direcional entre dois conceitos."""
        source = source_concept.strip().lower()
        target = target_concept.strip().lower()
        if source == target or not source or not target:
            return
        
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO knowledge_graph (source_concept, target_concept, weight, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(source_concept, target_concept) DO UPDATE SET
                        weight = MIN(5.0, weight + ?),
                        updated_at = ?
                ''', (source, target, weight, now, weight, now))
                conn.commit()
            logger.info(f"Relation added: {source} -> {target} (weight={weight})")
        except Exception as e:
            logger.error(f"Error adding relation to Knowledge Graph: {e}")

    def get_related_concepts(self, concept: str, min_weight: float = 0.5) -> List[Tuple[str, float]]:
        """Busca conceitos associados com peso maior ou igual ao mínimo."""
        val = concept.strip().lower()
        related = []
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    SELECT target_concept, weight FROM knowledge_graph
                    WHERE source_concept = ? AND weight >= ?
                    ORDER BY weight DESC
                ''', (val, min_weight))
                for row in c.fetchall():
                    related.append((row[0], row[1]))
        except Exception as e:
            logger.error(f"Error reading from Knowledge Graph: {e}")
        return related

    def traverse_graph(self, start_concept: str, max_depth: int = 2) -> List[str]:
        """Faz a travessia em largura (BFS) a partir de um conceito e retorna os conceitos alcançados."""
        visited = set()
        queue = [(start_concept.strip().lower(), 0)]
        
        while queue:
            node, depth = queue.pop(0)
            if not node:
                continue
            if node in visited:
                continue
            visited.add(node)
            
            if depth < max_depth:
                for target, _ in self.get_related_concepts(node):
                    if target not in visited:
                        queue.append((target, depth + 1))
        
        # Remove o nó inicial do conjunto retornado
        visited.discard(start_concept.strip().lower())
        return list(visited)
