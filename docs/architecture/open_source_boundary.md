# GOVERNANÇA E FRONTEIRA HEXAGONAL (OPEN SOURCE BOUNDARY)

Este documento define a fronteira arquitetural rígida e desacoplada do AI Revenue OS com base no padrão de design **Ports & Adapters (Arquitetura Hexagonal)**. Isso garante que o núcleo epistemológico e de negócios (**Cognitive Kernel**) permaneça puro, enquanto toda a infraestrutura e conectores de terceiros atuam como peças intercambiáveis.

---

## 🎯 1. Filosofia de Desenvolvimento

* **Foco Proprietário (Core)**: Tomada de decisão Bayesiana (`Beliefs`), avaliação estatística de dados empíricos (`Evidence`) e alocação de portfólios Bandit (`Decisions`).
* **Terceirização Open Source (Adapters)**: Persistência física de vetores (Qdrant), RAG (LlamaIndex), roteamento cíclico (LangGraph), orquestração transacional (Temporal/Prefect), mensageria (NATS/Kafka) e tracing (OpenTelemetry).
* **Inversão de Controle (IoC)**: O cérebro cognitivo nunca importa nem referencia diretamente adaptadores externos concretos. Ele conhece apenas as assinaturas abstratas (**Ports**). A resolução dos adaptadores ocorre dinamicamente através do `ProviderRegistry`.

---

## 🧠 2. Estrutura de Diretórios e Camadas

Para isolar as responsabilidades e garantir conformidade com a arquitetura hexagonal, o projeto é dividido em namespaces rígidos:

```text
src/
├── kernel/        # Cognitive Kernel (Crenças, Evidências, Decisões e APIs Facades)
├── ports/         # Interfaces abstratas de entrada/saída (Ports, Configs, IoC Registry)
├── adapters/      # Wrappers e implementações técnicas de terceiros (Qdrant, LiteLLM, LangGraph)
└── integrations/  # Conectores específicos de domínio de negócios (Pinterest, YouTube)
```

---

## 🔌 3. Camada de Portas & Inversão de Controle (`src/ports/`)

Todas as interações entre o Cognitive Kernel e serviços externos passam pela definição abstrata de uma porta (`ABC`). Nenhuma dependência estática de infraestrutura física é permitida no Kernel.

### A. Provider Registry (Mini IoC Container)
O **`ProviderRegistry`** em `src/ports/registry.py` gerencia o acoplamento dinâmico entre portas e adaptadores concretos.
* **Registro**: Os adaptadores são registrados no início da aplicação (ou em stubs de testes):
  ```python
  registry.register(MemoryPort, QdrantMemoryAdapter())
  ```
* **Resolução**: O Kernel resolve a capacidade sob demanda:
  ```python
  memory_adapter = registry.resolve(MemoryPort)
  ```
* **Capabilities**: O Kernel pode testar capacidades de forma dinâmica sem importar bibliotecas diretamente:
  ```python
  if registry.has_capability(BrowserPort):
      # executa automação
  ```

### B. Mapeamento de Portas e Capacidades
* **`MemoryPort`**: Abstração de busca semântica, persistência qualitativa e RAG.
* **`EmbeddingPort`**: Abstração de geração de embeddings densos (FastEmbed, OpenAI).
* **`LLMPort`**: Abstração de geração de texto bruto ou estruturado (LiteLLM, Ollama).
* **`WorkflowPort`**: Orquestração transacional de longa duração (Temporal, Prefect).
* **`EventPort`**: Barramento de eventos (SQLite, NATS, Redis Streams).
* **`BrowserPort`**: Automação e navegação em navegadores (Playwright, Browser Use, Stagehand).
* **`SearchPort`**: Pesquisa web (Tavily, Exa, Serper).
* **`DocumentPort`**: Ingestão e parseadores de arquivos estruturados (Docling).
* **`FeatureStorePort`**: Caching e fornecimento de variáveis temporais (Feast, SQLite cache).
* **`SecretPort`**: Gerenciamento de segredos e chaves (.env, Vault).
* **`CachePort`**: Caching transitivo (Redis, SQLite, In-Memory).
* **`SchedulerPort`**: Agendamentos e timers recorrentes (APScheduler, Temporal Schedules).

---

## 🔒 4. Diretrizes Invioláveis de Acoplamento

1. **Zero Imports Concretos no Kernel**: Nenhuma classe dentro de `src/kernel/` ou `src/cognition/` pode importar arquivos localizados em `src/adapters/` ou `src/integrations/`. Toda comunicação deve usar `src.ports` e resolução via `ProviderRegistry`.
2. **Configuration Isolation**: Configurações de infraestrutura são encapsuladas em dataclasses no módulo `src/ports/config.py` (`MemoryConfig`, `LLMConfig`, `WorkflowConfig`, etc.). O Kernel repassa a configuração correspondente ao iniciar os adaptadores, mantendo os parâmetros fora do cérebro.
3. **Resiliência e Fallbacks**: Testes locais devem rodar com sucesso usando adaptadores in-memory ou SQLite registrados no `ProviderRegistry` sem requerer serviços externos (Docker, chaves de API).
