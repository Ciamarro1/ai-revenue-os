import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class BasePublisher(ABC):
    """
    Interface abstrata obrigatória para todos os conectores de publicação determinísticos.
    """
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.sessions_dir = Path("config/sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.session_path = self.sessions_dir / f"{platform_name}.json"

    def get_session_path(self) -> Path:
        return self.session_path

    def has_session(self) -> bool:
        return self.session_path.exists()

    @abstractmethod
    def publish(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa o processo de publicação determinístico.
        Deve aceitar parâmetros como path da mídia, título, descrição, link e retornar um dicionário com status e URLs.
        """
        pass
