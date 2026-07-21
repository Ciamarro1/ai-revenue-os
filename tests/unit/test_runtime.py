import pytest
from src.runtime import Runtime, Lifecycle
from src.ports import ProviderRegistry, MemoryPort, EventPort
from src.core.kernel import CognitiveKernel
from src.revenue_os.analytics.database import ExperimentDatabase

def test_runtime_bootstrap_and_lifecycle():
    registry = ProviderRegistry()
    registry.clear()

    # 1. Setup sqlite in-memory db
    conn = ExperimentDatabase(":memory:")

    # 2. Bootstrap application runtime
    runtime = Runtime()
    kernel = runtime.bootstrap(conn)

    assert isinstance(kernel, CognitiveKernel)
    assert kernel.db == conn
    assert registry.has_capability(MemoryPort)
    assert registry.has_capability(EventPort)

    # 3. Audit health checks
    lifecycle = Lifecycle()
    health = lifecycle.health_check()
    assert health["status"] == "healthy"
    assert health["capabilities"]["memory"] == "connected"
    assert health["capabilities"]["event_bus"] == "connected"

    # 4. Initiate shutdown
    lifecycle.shutdown()
    assert not registry.has_capability(MemoryPort)
    assert not registry.has_capability(EventPort)

def test_lifecycle_degraded_status():
    registry = ProviderRegistry()
    registry.clear()

    # Empty registry results in degraded capability checks
    lifecycle = Lifecycle()
    health = lifecycle.health_check()
    assert health["status"] == "degraded"
    assert health["capabilities"]["memory"] == "missing"
    assert health["capabilities"]["event_bus"] == "missing"
