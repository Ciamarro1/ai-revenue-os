from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BrowserPort(ABC):
    """
    Browser Port interface.
    Decouples UI automation engines (Playwright, Browser Use, Stagehand).
    """
    @abstractmethod
    def navigate(self, url: str):
        """Navega para a URL especificada."""
        pass

    @abstractmethod
    def click(self, selector: str):
        """Clica no elemento correspondente ao seletor CSS/XPath."""
        pass

    @abstractmethod
    def type(self, selector: str, text: str):
        """Digita texto no campo especificado."""
        pass

    @abstractmethod
    def screenshot(self) -> bytes:
        """Tira uma captura de tela (screenshot) da janela ativa."""
        pass
