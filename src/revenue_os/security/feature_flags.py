import json
from pathlib import Path
from typing import Dict, Any, Optional

class SystemFeatureFlags:
    """
    Motor de Feature Flags de Sistema (Fase III Live Operations).
    Permite alternar dinamicamente comportamentos do Cérebro Econômico e Runtime
    sem alterar código ou reiniciar serviços (compatível com Unleash / Flagsmith).
    """

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            self.config_path = Path(__file__).parent.parent.parent.parent / "knowledge" / "feature_flags.json"
        else:
            self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.flags = self._load_or_create_default()

    def _load_or_create_default(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        defaults = {
            "knowledge_gain_weight_enabled": True,
            "adaptive_weights_enabled": True,
            "genome_mutation_enabled": False,
            "live_trading_enabled": False,
            "circuit_breaker_enabled": True,
            "auto_recovery_enabled": True,
            "exploration_rate": 0.30,
            "environment": "development"
        }
        self.save(defaults)
        return defaults

    def is_feature_enabled(self, feature_key: str, default: bool = False) -> bool:
        return bool(self.flags.get(feature_key, default))

    def get_parameter(self, param_key: str, default: Any = None) -> Any:
        return self.flags.get(param_key, default)

    def set_feature(self, feature_key: str, enabled: bool) -> None:
        self.flags[feature_key] = enabled
        self.save(self.flags)

    def save(self, flags: Dict[str, Any]) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(flags, f, indent=2, ensure_ascii=False)
