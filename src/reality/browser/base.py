from abc import ABC, abstractmethod
from typing import Dict, Any

class BrowserClient(ABC):
    """
    Interface base universal para o Browser Worker.
    Focado em inicializar instâncias (via Playwright, Browser Use, Selenium)
    para interações onde a API oficial não existe ou é muito limitante.
    """
    
    @abstractmethod
    def launch(self) -> None:
        """Inicializa o navegador/worker."""
        pass
        
    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Informa se a automação está funcional (drivers ok, sem capcthas hard)."""
        pass
        
    @abstractmethod
    def session(self) -> Any:
        """Retorna o contexto ou página ativa para operações."""
        pass
        
    @abstractmethod
    def close(self) -> None:
        """Encerra graciosamente a automação."""
        pass
