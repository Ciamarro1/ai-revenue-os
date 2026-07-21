from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import json
import os

@dataclass
class MemoryConfig:
    provider: str = "sqlite"
    connection_string: str = ":memory:"
    collection_name: str = "memories"
    qdrant_host: Optional[str] = None
    qdrant_port: Optional[int] = None

@dataclass
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    temperature: float = 0.7

@dataclass
class SearchConfig:
    provider: str = "tavily"
    api_key: Optional[str] = None

@dataclass
class WorkflowConfig:
    provider: str = "temporal"
    host: str = "localhost"
    port: int = 7233

@dataclass
class EventConfig:
    provider: str = "sqlite"
    connection_string: str = ":memory:"

@dataclass
class BrowserConfig:
    provider: str = "playwright"
    headless: bool = True

@dataclass
class KernelConfig:
    env: str = "development"
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    event: EventConfig = field(default_factory=EventConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    extra: Dict[str, Any] = field(default_factory=dict)
    
    # Dicionário do manifesto de capacidades: mapeia Capability -> Adapter
    providers: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "memory.semantic": {"adapter": "sqlite", "enabled": True},
        "llm.chat": {"adapter": "openai", "enabled": True},
        "browser": {"adapter": "playwright", "enabled": True},
        "search.web": {"adapter": "tavily", "enabled": True},
        "embedding": {"adapter": "hash", "enabled": True},
        "event": {"adapter": "sqlite", "enabled": True}
    })

    def load_manifest(self, filepath: str = "capability_manifest.json"):
        """Tenta carregar o manifesto de capacidades de um arquivo JSON."""
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "providers" in data:
                        self.providers.update(data["providers"])
            except Exception:
                pass
