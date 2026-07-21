import pytest
import json
import os
from src.ports import ProviderRegistry, Capabilities, KernelConfig, MemoryPort
from src.runtime import Runtime
from src.revenue_os.analytics.database import ExperimentDatabase

def test_capabilities_enum_and_registry():
    registry = ProviderRegistry()
    registry.clear()

    # Capabilities can be used as keys directly
    assert isinstance(Capabilities.MEMORY_SEMANTIC, str)
    assert Capabilities.MEMORY_SEMANTIC.value == "memory.semantic"

    # Register using Enum
    registry.register(Capabilities.MEMORY_SEMANTIC, "semantic-adapter-mock")
    assert registry.has_capability(Capabilities.MEMORY_SEMANTIC)
    assert registry.resolve(Capabilities.MEMORY_SEMANTIC) == "semantic-adapter-mock"

    # Clean up
    registry.clear()

def test_load_manifest_fallback_and_json():
    # Verify default fallback mappings
    config = KernelConfig()
    assert config.providers["memory.semantic"]["adapter"] == "sqlite"

    # Create dummy JSON manifest file
    filepath = "dummy_manifest.json"
    manifest_data = {
        "providers": {
            "memory.semantic": {"adapter": "qdrant", "enabled": True},
            "llm.chat": {"adapter": "litellm", "enabled": True}
        }
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    try:
        config.load_manifest(filepath)
        # Verify JSON overrides
        assert config.providers["memory.semantic"]["adapter"] == "qdrant"
        assert config.providers["llm.chat"]["adapter"] == "litellm"
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
