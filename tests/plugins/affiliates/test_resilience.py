import pytest
import time
from src.revenue_os.plugins.affiliates.resilience import (
    TokenBucketRateLimiter,
    ExponentialBackoffRetry,
    CircuitBreaker
)

def test_token_bucket_rate_limiter():
    limiter = TokenBucketRateLimiter(capacity=2.0, refill_rate_per_sec=10.0)
    assert limiter.acquire(1.0) is True
    assert limiter.acquire(1.0) is True
    assert limiter.acquire(1.0) is False  # Esgotou tokens

def test_exponential_backoff_retry():
    retry = ExponentialBackoffRetry(max_retries=2, backoff_factor=0.01, jitter=False)
    
    attempts = [0]
    def flaky():
        attempts[0] += 1
        if attempts[0] < 2:
            raise ValueError("Transient error")
        return "success"

    res = retry.execute(flaky)
    assert res == "success"
    assert attempts[0] == 2

def test_circuit_breaker_states():
    cb = CircuitBreaker(failure_threshold=2, recovery_time_sec=0.2)
    assert cb.state == "CLOSED"
    
    def failing():
        raise RuntimeError("Fail")
        
    # Falha 1
    with pytest.raises(RuntimeError):
        cb.execute(failing)
    assert cb.state == "CLOSED"
    
    # Falha 2 -> muda para OPEN
    with pytest.raises(RuntimeError):
        cb.execute(failing)
    assert cb.state == "OPEN"
    
    # Enquanto OPEN, bloqueia execuções imediatamente
    with pytest.raises(RuntimeError, match="CircuitBreaker is OPEN"):
        cb.execute(lambda: "ok")
        
    # Aguardar tempo de recuperação
    time.sleep(0.25)
    
    def success():
        return "recovered"
        
    # Execução em HALF_OPEN recupera para CLOSED
    res = cb.execute(success)
    assert res == "recovered"
    assert cb.state == "CLOSED"
