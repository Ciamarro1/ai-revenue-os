from pydantic import BaseModel, Field

class AffiliatePluginConfig(BaseModel):
    """
    Configuração do módulo de afiliados com Pydantic v2.
    """
    # Feature Flags
    enable_hotmart: bool = True
    enable_kiwify: bool = True
    enable_eduzz: bool = True
    enable_amazon: bool = True

    # Resiliência
    rate_limit_requests_per_minute: int = 60
    max_retries: int = 3
    retry_backoff_factor: float = 1.5
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_time_seconds: float = 30.0
    request_timeout_seconds: float = 5.0
