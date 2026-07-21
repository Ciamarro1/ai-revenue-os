"""
LlamaIndex Adapter — Document Ingestion Layer.

Abstrai a construção de nós de documentos estruturados para indexação
semântica. Quando LlamaIndex não está instalado, opera como um
wrapper transparente que delega ao Qdrant diretamente.
"""
import logging
from typing import Any, List, Dict, Optional

logger = logging.getLogger(__name__)

# Tenta importar LlamaIndex (dependência futura opcional)
_LLAMAINDEX_AVAILABLE = False
try:
    from llama_index.core import Document
    _LLAMAINDEX_AVAILABLE = True
except ImportError:
    Document = None


def is_llamaindex_available() -> bool:
    """Retorna True se o LlamaIndex está instalado."""
    return _LLAMAINDEX_AVAILABLE


class LlamaIndexAdapter:
    """
    Adapter para o LlamaIndex framework.

    Responsável por:
      - Converter textos brutos em nós estruturados com metadados.
      - Preparar documentos para indexação no Qdrant via retriever.

    Quando LlamaIndex não está disponível, retorna os documentos como
    dicionários simples para processamento direto pelo Qdrant adapter.
    """
    def __init__(self, vector_store: Any = None):
        self.vector_store = vector_store

    def create_document(
        self, text_content: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria um documento estruturado a partir de texto bruto.
        Retorna um dict com 'content' e 'metadata' independente do backend.
        """
        if _LLAMAINDEX_AVAILABLE and Document is not None:
            doc = Document(text=text_content, metadata=metadata)
            return {
                "content": doc.text,
                "metadata": doc.metadata,
                "doc_id": doc.doc_id,
            }
        # Fallback: dict simples
        return {
            "content": text_content,
            "metadata": metadata,
            "doc_id": None,
        }

    def parse_documents(
        self, texts: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Converte uma lista de textos em documentos estruturados.
        """
        if metadata_list is None:
            metadata_list = [{}] * len(texts)

        return [
            self.create_document(text, meta)
            for text, meta in zip(texts, metadata_list)
        ]
