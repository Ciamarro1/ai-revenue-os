import pytest
from src.ports import ProviderRegistry, MemoryPort

class DummyMemoryAdapter(MemoryPort):
    def store(self, content, memory_type, metadata):
        return "dummy-id"
    def search(self, query, limit=5):
        return [{"content": "dummy"}]
    def retrieve_context(self, entity, limit=3):
        return "dummy context"

def test_registry_registration_and_resolution():
    registry = ProviderRegistry()
    registry.clear()

    # Registry has no capability initially
    assert not registry.has_capability(MemoryPort)
    with pytest.raises(ValueError):
        registry.resolve(MemoryPort)

    # Register dummy adapter
    adapter = DummyMemoryAdapter()
    registry.register(MemoryPort, adapter)

    # Verify resolution
    assert registry.has_capability(MemoryPort)
    resolved = registry.resolve(MemoryPort)
    assert resolved == adapter
    assert resolved.store("test", "test", {}) == "dummy-id"

    # Verify clear
    registry.clear()
    assert not registry.has_capability(MemoryPort)
