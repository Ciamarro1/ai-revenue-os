import os
import json
import time
import logging
from typing import Dict, Optional
from pathlib import Path

from src.revenue_os.analytics.database import ExperimentDatabase

logger = logging.getLogger("revenue_os.feature_flags")

class FeatureFlags:
    """
    Sistema centralizado de Feature Flags.
    Prioridade: DB override > JSON file > defaults.
    Cache de 60s para evitar I/O excessivo.
    """
    
    DEFAULTS: Dict[str, bool] = {
        "ENABLE_PLAYWRIGHT": True,
        "ENABLE_BROWSER_USE": True,
        "ENABLE_OPENMANUS": True,
        "ENABLE_RATE_LIMITER": True,
        "ENABLE_TRUST_SCORE": True,
        "ENABLE_AUTO_RAMPUP": True,
        "ENABLE_SMART_SCHEDULING": False,
        "ENABLE_BOARD_TRACKING": True,
        "ENABLE_IMAGE_HASH": True,
        "ENABLE_QUEUE_PUBLISHER": True,
        "ENABLE_MLFLOW_TIMING": True,
        "ENABLE_EXPONENTIAL_BACKOFF": True,
        "ENABLE_FLUX": True,
        "ENABLE_EDGE_TTS": True,
        "ENABLE_MPT": True,
    }
    
    _DB_KEY = "FEATURE_FLAGS"
    _CACHE_TTL = 60  # seconds
    
    def __init__(self, db: Optional[ExperimentDatabase] = None, config_path: Optional[str] = None):
        self.db = db
        if config_path:
            self._config_path = Path(config_path)
        else:
            project_root = Path(__file__).parent.parent.parent.parent
            self._config_path = project_root / "config" / "feature_flags.json"
        self._cache: Dict[str, bool] = {}
        self._cache_time: float = 0.0
        self._load()
    
    def _load(self):
        """Carrega flags: defaults → JSON → DB override."""
        merged = dict(self.DEFAULTS)
        
        # Layer 2: JSON file
        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    json_flags = json.load(f)
                for k, v in json_flags.items():
                    if isinstance(v, bool):
                        merged[k] = v
            except Exception as e:
                logger.warning(f"Erro ao carregar feature_flags.json: {e}")
        
        # Layer 3: DB override (highest priority)
        if self.db:
            try:
                db_flags = self.db.get_system_state(self._DB_KEY)
                if db_flags and isinstance(db_flags, dict):
                    for k, v in db_flags.items():
                        if isinstance(v, bool):
                            merged[k] = v
            except Exception as e:
                logger.warning(f"Erro ao carregar flags do DB: {e}")
        
        self._cache = merged
        self._cache_time = time.time()
    
    def _ensure_fresh(self):
        """Recarrega o cache se expirou."""
        if time.time() - self._cache_time > self._CACHE_TTL:
            self._load()
    
    def is_enabled(self, flag_name: str) -> bool:
        """Retorna True se a flag está ativa. False para flags desconhecidas."""
        self._ensure_fresh()
        return self._cache.get(flag_name, False)
    
    def get_all(self) -> Dict[str, bool]:
        """Retorna todas as flags ativas."""
        self._ensure_fresh()
        return dict(self._cache)
    
    def set_override(self, flag_name: str, value: bool):
        """Grava override no DB (system_state). Requer DB."""
        if not self.db:
            raise RuntimeError("FeatureFlags: DB não configurado para set_override")
        
        db_flags = self.db.get_system_state(self._DB_KEY) or {}
        db_flags[flag_name] = value
        self.db.set_system_state(self._DB_KEY, db_flags)
        
        # Invalidate cache
        self._cache[flag_name] = value
        logger.info(f"Feature flag override: {flag_name} = {value}")
    
    def remove_override(self, flag_name: str):
        """Remove override do DB, volta ao valor do JSON/default."""
        if not self.db:
            return
        db_flags = self.db.get_system_state(self._DB_KEY) or {}
        db_flags.pop(flag_name, None)
        self.db.set_system_state(self._DB_KEY, db_flags)
        self._cache_time = 0.0  # Force reload
