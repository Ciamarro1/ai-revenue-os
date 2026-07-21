# CATÁLOGO DE CAPACIDADES (CAPABILITIES.md)

Este catálogo documenta os enums oficiais do sistema (`src/ports/capabilities.py`) e as interfaces abstratas (Ports) às quais eles correspondem.

---

## 🗂️ 1. Mapeamento de Capacidades (Enums & Ports)

| Chave Enum (`Capabilities`) | Valor String | Interface Port (`src/ports/`) | Descrição e Utilidade |
| :--- | :--- | :--- | :--- |
| `MEMORY_SEMANTIC` | `"memory.semantic"` | `MemoryPort` | Armazenamento e busca por similaridade semântica em textos qualitativos (ex. hooks vencedores). |
| `MEMORY_EPISODIC` | `"memory.episodic"` | `MemoryPort` | Registro histórico de sequências operacionais ocorridas no tempo. |
| `MEMORY_GRAPH` | `"memory.graph"` | `MemoryPort` | Armazenamento de relações de dependência qualitativa entre hipóteses e causas. |
| `SEARCH_WEB` | `"search.web"` | `SearchPort` | Consultas e raspagem de dados em buscadores abertos (ex. Tavily, Brave Search). |
| `SEARCH_INTERNAL` | `"search.internal"` | `SearchPort` | Consultas em base interna de conhecimentos do sistema. |
| `BROWSER` | `"browser"` | `BrowserPort` | Automação e navegação programática simulando ações humanas em navegadores. |
| `EMBEDDING` | `"embedding"` | `EmbeddingPort` | Vetorização de textos (Embeddings) para indexação semântica (ex. FastEmbed, OpenAI). |
| `LLM_CHAT` | `"llm.chat"` | `LLMPort` | Interação conversacional direta com Modelos de Linguagem (ex. LiteLLM, OpenAI). |
| `LLM_REASONING` | `"llm.reasoning"` | `LLMPort` | Agenciamento e cadeias de raciocínio lógico estruturado (ex. Claude, DeepSeek). |
| `SECRET` | `"secret"` | `SecretPort` | Gerenciamento e carregamento de chaves de API e segredos operacionais (.env, Vault). |
| `CACHE` | `"cache"` | `CachePort` | Caching transitivo rápido em memória ou chaves-valor (ex. Redis, SQLite). |
| `SCHEDULER` | `"scheduler"` | `SchedulerPort` | Execução recorrente e agendamentos de jobs (APScheduler, Cron). |
| `WORKFLOW` | `"workflow"` | `WorkflowPort` | Orquestração transacional durável e persistente de longo prazo (Temporal, Prefect). |
| `AGENT` | `"agent"` | `AgentPort` | Roteamento e loops cíclicos de conselhos de múltiplos agentes com estado (LangGraph). |
| `FEATURE_STORE` | `"feature_store"` | `FeatureStorePort` | Disponibilização de variáveis temporais estruturadas para cálculo estatístico (Feast). |
| `DOCUMENT` | `"document"` | `DocumentPort` | Parseamento e conversão de arquivos para estruturação RAG (Docling). |
| `EVENT` | `"event"` | `EventPort` | Barramento de pub-sub interno síncrono e assíncrono (SQLite, NATS). |

---

## 🛠️ 2. Verificação de Capacidade em Runtime

O Kernel cognitivo ou qualquer agente pode testar a disponibilidade de uma capacidade antes de sua execução para permitir falhas controladas e graceful degradation:

```python
from src.ports import ProviderRegistry, Capabilities

registry = ProviderRegistry()

if registry.has_capability(Capabilities.BROWSER):
    browser = registry.resolve(Capabilities.BROWSER)
    browser.navigate("https://pinterest.com")
else:
    logger.warning("Browser automation is disabled or missing adapter.")
```
