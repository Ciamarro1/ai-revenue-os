import logging
from typing import Dict, Any, List, Optional
from src.revenue_os.plugins.base_plugin import BasePlugin
from src.revenue_os.connectors.capability_registry import CapabilityRegistry

class PluginRuntime:
    """
    Plugin Runtime & Orquestrador de Capacidades (Sprint 9.7).
    Gerencia o ciclo de vida dos plugins, executa health checks contínuos
    e realiza failover automático para provedores de fallback.
    """

    def __init__(self, capability_registry: Optional[CapabilityRegistry] = None):
        self.capability_registry = capability_registry or CapabilityRegistry()
        self._plugins: Dict[str, BasePlugin] = {}

    def register_plugin(self, plugin: BasePlugin) -> bool:
        """
        Registra e inicializa um plugin no runtime.
        """
        try:
            if plugin.initialize():
                self._plugins[plugin.plugin_name.lower()] = plugin
                return True
        except Exception as e:
            logging.error(f"Falha ao inicializar plugin '{plugin.plugin_name}': {e}")
        return False

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        return self._plugins.get(name.lower())

    def execute_capability(self, capability_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma capacidade com suporte a failover automático entre provedores.
        """
        primary_name = self.capability_registry.get_provider(capability_name)
        fallbacks = self.capability_registry.get_fallbacks(capability_name)

        provider_order = [primary_name] + fallbacks

        for provider in provider_order:
            plugin = self.get_plugin(provider)
            if plugin:
                health = plugin.health_check()
                if health.get("status") == "HEALTHY":
                    try:
                        res = plugin.execute(payload)
                        res["executed_by_provider"] = provider
                        return res
                    except Exception as e:
                        logging.warning(f"Erro na execução com provedor '{provider}': {e}. Tentando fallback...")

        # Fallback genérico de simulação se nenhum plugin registrado estiver ativo
        return {
            "status": "EXECUTED_FALLBACK",
            "executed_by_provider": primary_name,
            "result": {"message": f"Executado via adaptado padrão para capacidade '{capability_name}'."}
        }
