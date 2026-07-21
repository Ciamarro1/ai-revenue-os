# MAPA DE AQUISIÇÕES OPEN SOURCE (OPEN SOURCE ACQUISITION MAP)

Este documento estabelece as diretrizes estratégicas para integrar soluções open source maduras e de mercado na infraestrutura do **AI Revenue OS**, definindo a fronteira entre a inteligência proprietária (**Cognitive Kernel**) e os adaptadores de infraestrutura e orquestração commodity.

---

## 🎯 1. Filosofia de Integração

O princípio orientador do projeto é: **Não reinventar a roda**.
* **Proprietário (O Cérebro)**: Mantemos e evoluímos internamente a modelagem epistemológica de crenças, a inteligência de avaliação de qualidade de evidências e as políticas estatísticas de tomada de decisão.
* **Commodity (Os Membros e Sensores)**: Acoplamos e integramos projetos open source consolidados para resolver fluxos de trabalho (workflows), roteamento de agentes, captura de métricas analíticas, rastreamento de decisões e banco vetorial de longo prazo.
* **Ports & Adapters**: Todas as bibliotecas externas e frameworks de terceiros são integrados como **Adapters** que implementam **Ports** abstratas definidas em `src/ports/`.

---

## 📊 2. Matriz de Prioridade de Aquisição

Mapeamos a utilidade e prioridade de integração de cada tecnologia open-source selecionada para guiar os próximos passos lógicos:

| Prioridade | Projeto / Tecnologia | Função Operacional | Nível de Integração |
| :--- | :--- | :--- | :--- |
| ⭐⭐⭐⭐⭐ | **LangGraph** | Roteamento cíclico e execução de todos os agentes | Implementação do `AgentPort` |
| ⭐⭐⭐⭐⭐ | **Temporal.io** / **Prefect** | Orquestração de workflows distribuídos e persistentes | Implementação do `WorkflowPort` |
| ⭐⭐⭐⭐⭐ | **LiteLLM** | Unificação de chamadas de LLM (OpenAI, Anthropic, Gemini) | Implementação do `LLMPort` |
| ⭐⭐⭐⭐⭐ | **FastEmbed** | Vetorização local de alta performance em CPU | Implementação do `EmbeddingPort` |
| ⭐⭐⭐⭐⭐ | **Docling** | Conversão de PDF/DOCX/HTML para formato RAG | Implementação do `DocumentPort` |
| ⭐⭐⭐⭐⭐ | **OpenTelemetry** | Coleta de telemetria e traces das ações | Implementação do `MetricsPort` |
| ⭐⭐⭐─☆ | **Grafana + Loki + Tempo** | Visualização e auditoria de spans de decisão | Visualização de logs e traces |
| ⭐⭐⭐─☆ | **Neo4j** | Representação relacional causal de hipóteses | Memória semântica causal |
| ⭐⭐⭐─☆ | **Feast** | Fornecimento centralizado de features temporais | Implementação do `FeatureStorePort` |
| ⭐⭐⭐─☆ | **MLflow** | Tracking estatístico de parâmetros experimentais | Registro e versionamento de testes |
| ⭐⭐──☆ | **Browser Use** / **Stagehand** | Automação e navegação web resiliente com LLM | Implementação do `BrowserPort` |

---

## 🧩 3. Mapeamento Estrutural das Portas & Adapters

### A. LLM & Modelos (LiteLLM)
* **Porta**: `LLMPort`
* **Adapter**: `LiteLLMAdapter` em `src/adapters/litellm/`
* **Função**: Resolve todas as chamadas de inferência de texto brutas e estruturadas usando LiteLLM para interoperabilidade entre OpenAI, Anthropic, Gemini, Groq e Ollama.

### B. Memória Vetorial (LlamaIndex + Qdrant + Docling)
* **Porta**: `MemoryPort` e `DocumentPort`
* **Adapter**: `LlamaIndexAdapter` em `src/adapters/llamaindex/` e `DoclingAdapter` em `src/adapters/docling/`
* **Função**: Ingestão de arquivos com Docling, armazenamento de embeddings densos com Qdrant e recuperação contextual com LlamaIndex.

### C. Roteamento de Agentes (LangGraph)
* **Porta**: `AgentPort`
* **Adapter**: `LangGraphAgentAdapter` em `src/adapters/langgraph/`
* **Função**: Gerencia o runtime cíclico com estado de agentes. O grafo consulta a fachada do kernel para obter decisões autoritativas.

### D. Workflows de Longa Duração (Temporal / Prefect)
* **Porta**: `WorkflowPort`
* **Adapter**: `TemporalWorkflowAdapter` em `src/adapters/temporal/`
* **Função**: Controla a persistência durável e retries automáticos de transações longas (testes A/B que duram semanas).

---

## 🛠️ 4. Cronograma de Alinhamento do Roadmap

A ordem de implementação das próximas sprints seguirá a matriz de prioridades estabelecida:
1. **Sprint 5.11 (Hexagonal Restructuring & IoC)**: Reestruturar diretórios, introduzir `ProviderRegistry`, configs e novos ports (Secret, Cache, Scheduler).
2. **Sprint 6 (Agent Runtime Layer)**: Integrar **LangGraph** para o conselho completo de agentes cíclicos.
3. **Sprint 7 (Autonomous Workflows)**: Integrar **Temporal / Prefect** para os fluxos longos de testes.
4. **Sprint 8 (Observability Layer)**: Integrar **OpenTelemetry + Grafana Stack** para tracing cognitivo.
5. **Sprint 9 (Experiment Intelligence & Feature Store)**: Integrar **MLflow + Feast Feature Store + Neo4j**.
6. **Sprint 10 (Actuators & Distribution OS)**: Integrar **n8n + Browser Use / Stagehand** para atuações físicas externas.
