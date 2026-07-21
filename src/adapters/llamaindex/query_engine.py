"""
LlamaIndex Query Engine — Context Generator.

Orquestra a recuperação semântica e formata os resultados em blocos
contextuais prontos para injeção nos prompts dos agentes.
"""
import logging
from typing import List, Dict, Any, Optional

from src.adapters.llamaindex.retriever import SemanticRetriever

logger = logging.getLogger(__name__)


class ContextQueryEngine:
    """
    Motor de consulta contextual que converte resultados de busca
    semântica em texto formatado para o LLM.
    """
    def __init__(self, retriever: SemanticRetriever):
        self.retriever = retriever

    def query(self, question: str, top_k: int = 3) -> str:
        """
        Executa busca semântica e formata os resultados em um bloco
        de contexto pronto para inserção no prompt.
        """
        results = self.retriever.retrieve(question, top_k=top_k)

        if not results:
            return "Nenhuma memória semântica relevante encontrada no Qdrant."

        blocks = []
        for idx, r in enumerate(results, 1):
            meta = r.get("metadata", {})
            meta_str = ", ".join(f"{k}: {v}" for k, v in meta.items()) if meta else "N/A"
            score_pct = f"{r['score']:.0%}"
            blocks.append(
                f"[{idx}] (Relevância: {score_pct}) {r['content']}\n"
                f"    Metadados: {{{meta_str}}}"
            )

        return "\n".join(blocks)

    def query_with_metadata(
        self, question: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retorna resultados brutos com metadados completos
        para consumo programático pelos agentes.
        """
        return self.retriever.retrieve(question, top_k=top_k)


