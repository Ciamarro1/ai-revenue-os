import logging
from typing import Dict, List, Optional
from src.revenue_os.plugins.research.providers.base_provider import OpportunityProvider

class ProviderRegistry:
    """
    Registro dinâmico de Provedores de Oportunidades.
    Permite adicionar novos adaptadores em tempo de execução sem modificar código existente.
    """

    def __init__(self):
        self._providers: Dict[str, OpportunityProvider] = {}

    def register(self, provider: OpportunityProvider) -> None:
        name = provider.provider_name.lower()
        self._providers[name] = provider
        logging.info(f"[ProviderRegistry] Provedor '{name}' registrado com sucesso.")

    def unregister(self, name: str) -> None:
        name = name.lower()
        if name in self._providers:
            del self._providers[name]
            logging.info(f"[ProviderRegistry] Provedor '{name}' removido.")

    def get(self, name: str) -> Optional[OpportunityProvider]:
        return self._providers.get(name.lower())

    def list_all(self) -> List[OpportunityProvider]:
        return list(self._providers.values())

    def list_active(self) -> List[OpportunityProvider]:
        return [p for p in self._providers.values() if p.is_enabled]
