import time
import random
import logging
from typing import Callable, Any, Dict

class TokenBucketRateLimiter:
    """
    Limitador de taxa usando o algoritmo Token Bucket.
    """
    def __init__(self, capacity: float = 60.0, refill_rate_per_sec: float = 1.0):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        self.tokens = capacity
        self.last_refill = time.time()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def acquire(self, tokens: float = 1.0) -> bool:
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def get_available_tokens(self) -> float:
        self._refill()
        return round(self.tokens, 2)


class ExponentialBackoffRetry:
    """
    Mecanismo de repetição com Backoff Exponencial e Jitter.
    """
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.5, jitter: bool = True):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        attempt = 0
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                if attempt > self.max_retries:
                    logging.error(f"[Retry] Limite de {self.max_retries} tentativas excedido: {e}")
                    raise e
                
                sleep_time = (self.backoff_factor ** attempt)
                if self.jitter:
                    sleep_time += random.uniform(0, 0.5)
                
                logging.warning(f"[Retry] Tentativa {attempt}/{self.max_retries} falhou ({e}). Aguardando {sleep_time:.2f}s...")
                time.sleep(sleep_time)


class CircuitBreaker:
    """
    Máquina de Estados de Circuit Breaker (CLOSED, OPEN, HALF_OPEN).
    """
    def __init__(self, failure_threshold: int = 5, recovery_time_sec: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_time_sec = recovery_time_sec
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.last_state_change = time.time()

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        now = time.time()

        if self.state == "OPEN":
            if now - self.last_state_change > self.recovery_time_sec:
                self.state = "HALF_OPEN"
                self.last_state_change = now
                logging.info("[CircuitBreaker] Estado alterado para HALF_OPEN. Testando recuperação...")
            else:
                raise RuntimeError("CircuitBreaker is OPEN. Execução bloqueada temporariamente.")

        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                self.last_state_change = now
                logging.info("[CircuitBreaker] Estado alterado para CLOSED. Serviço recuperado.")
            return result
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                self.last_state_change = now
                logging.error(f"[CircuitBreaker] Estado alterado para OPEN após {self.failure_count} falhas: {e}")
            raise e
