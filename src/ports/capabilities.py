from enum import Enum

class Capabilities(str, Enum):
    """
    Capabilities Enum for AI Revenue OS.
    Standardizes keys for dynamic capability registration and resolution.
    """
    MEMORY_SEMANTIC = "memory.semantic"
    MEMORY_EPISODIC = "memory.episodic"
    MEMORY_GRAPH = "memory.graph"
    MEMORY_VECTOR = "memory.vector"

    SEARCH_WEB = "search.web"
    SEARCH_INTERNAL = "search.internal"

    BROWSER = "browser"
    EMBEDDING = "embedding"
    LLM_CHAT = "llm.chat"
    LLM_REASONING = "llm.reasoning"

    SECRET = "secret"
    CACHE = "cache"
    SCHEDULER = "scheduler"
    WORKFLOW = "workflow"
    AGENT = "agent"
    FEATURE_STORE = "feature_store"
    DOCUMENT = "document"
    EVENT = "event"
