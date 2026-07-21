from abc import ABC, abstractmethod
from typing import Dict, Any

class DocumentPort(ABC):
    """
    Document Port interface.
    Decouples document parsing and loaders (Docling, Unstructured, Marker).
    """
    @abstractmethod
    def parse_document(self, file_path: str) -> str:
        """Lê um arquivo (PDF, HTML, DOCX) e retorna o conteúdo convertido em Markdown estruturado."""
        pass
