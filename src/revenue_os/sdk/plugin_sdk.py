from typing import Dict, Any, Optional
from datetime import datetime, timezone

class PluginContext:
    """
    Contexto isolado passado para a execução de um Plugin no PluginRuntime.
    """
    def __init__(self, experiment_id: str, payload: Dict[str, Any], environment: str = "production"):
        self.experiment_id = experiment_id
        self.payload = payload
        self.environment = environment
        self.timestamp = datetime.now(timezone.utc).isoformat() + "Z"

class PluginLogger:
    """
    Logger padronizado para plugins com suporte a mascaramento automático pelo SecretsManager.
    """
    @staticmethod
    def info(plugin_name: str, message: str) -> str:
        return f"[PLUGIN_INFO][{plugin_name}] {message}"

    @staticmethod
    def error(plugin_name: str, error_msg: str) -> str:
        return f"[PLUGIN_ERROR][{plugin_name}] {error_msg}"
