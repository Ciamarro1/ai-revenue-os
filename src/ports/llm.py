from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMPort(ABC):
    """
    LLM Port interface.
    Decouples LLM providers (OpenAI, Anthropic, Gemini, LiteLLM, Ollama).
    """
    @abstractmethod
    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Gera uma resposta em formato texto bruto a partir de um prompt."""
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, schema: Any, system_instruction: Optional[str] = None) -> Any:
        """Gera uma resposta estruturada de acordo com um schema (Pydantic / JSON Schema)."""
        pass
