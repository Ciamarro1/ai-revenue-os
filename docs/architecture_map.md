# AI Revenue OS: Inventário Exaustivo de Arquivos e Artefatos

Este documento fornece o mapeamento completo e o detalhamento de cada arquivo e diretório do projeto, descrevendo o propósito de sua existência no laboratório autônomo.

---

## 📁 Raiz do Projeto (Configuração e Metadados)

* **`.env` e `.env.example`**: Definição de tokens de API e chaves de segurança.
* **`.gitignore`**: Lista de pastas temporárias e cache ignoradas pelo Git.
* **`CHANGELOG.md`**: Histórico cronológico de versões e novas implementações.
* **`CONTRIBUTING.md` e `MANIFESTO.md`**: Filosofia quant e regras de contribuição.
* **`LICENSE` e `PRIVACY.md` e `SECURITY.md`**: Termos legais e segurança.
* **`README.md`**: Porta de entrada e guia rápido de instalação e comandos de execução.
* **`pyproject.toml`**: Gerenciador moderno de empacotamento Python (`ai-revenue-os`).
* **`GEMINI.md`**: O arquivo de contexto de sessão que mapeia os caminhos de documentação e as regras invioláveis.
* **`prod_db.sqlite3`**: Banco de dados relacional de produção.

---

## 📁 `docs/` (Centro de Conhecimento e Governança)

O diretório `/docs/` foi expandido em v2.0/v2.1 em 10 subpastas para descentralizar e estruturar o conhecimento consumido por agentes:

### 1. `docs/agent/` (Como o agente pensa)
* **`constitution.md`**: Diretrizes de identidade do Chief Cognitive Engineer, missão e critérios de conclusão.
* **`prompt_patterns.md`**: Padrões de prompt e diretrizes de RAG cognitivo.
* **`agent_roles.md`**: Responsabilidades estruturadas dos papéis dos agentes (Architect, Researcher, etc.).
* **`mcp_servers.md`**: Ferramentas e regras de utilização dos servidores MCP.
* **`architecture.md`**: Mapeamento das camadas do sistema.

### 2. `docs/knowledge/` (O que o projeto sabe)
* **`project_map.md`**: Mapeamento dos arquivos e banco de dados SQLite.
* **`roadmap.md`**: Roadmap operacional de sprints.
* **`tech_stack.md`**: Stack atual e stack preferencial de evolução.
* **`glossary.md`**: Glossário de termos e métricas estatísticas (MAB, p-values, Stop-Loss).
* **`repository_learning.md`**: Log de lições aprendidas (Playwright viewports, trust score decréscimo).

### 3. `docs/experiments/` (Como experimenta)
* **`experimentation_protocol.md`**: Modelagem de hipóteses, variantes A/B e regras de validação estatística.

### 4. `docs/architecture/` (Fronteiras, Especificações e Governança)
* **`open_source_first.md`**: Diretriz fundamental *Open Source First. Build Only the Differentiator*.
* **`open_source_boundary.md`**: Mapeamento de fronteiras e orquestração.
* **`capability_map.md`**: Mapa de Capacidades desacoplado.
* **`specification_suite.md`**: Suíte de especificações congeladas.
* **`oss_capability_matrix.md`**: Matriz de Homologação de Capacidades Open Source (v4.0).
* **`evidence_driven_development.md`**: As 5 regras de governança do Evidence Driven Development (v4.5).
* **`kernel_lock.md`**: Política de Kernel Lock v1.0 e Zero-Kernel Modification (v5.0).
* **`definition_of_done.md`**: Os 7 critérios do Definition of Done para homologação de produção (v5.5).
* **`production_evidence.md`**: Framework de Evidências em Produção PE-1 a PE-10 (v6.5).

### 5. `docs/research/` (O que foi pesquisado)
* **`research_protocol.md`**: Protocolo de checagem técnica e APIs antes do desenvolvimento.
* **`open_source_acquisition_map.md`**: Mapa de aquisições de ferramentas open source.

### 5. `docs/adr/` (Decisões tomadas)
* **`decision_log.md`**: ADRs históricas (ADR 001 - 013).

### 6. `docs/playbooks/` (Processos recorrentes)
* **`engineering_playbook.md`**: Avaliação de escolhas baseada nos 6 pilares de engenharia.
* **`evaluation_protocol.md`**: Suite de pytest, drift check e limites de performance de renderização.

### 7. `docs/standards/` (Regras de engenharia)
* **`coding_standards.md`**: Padrões de escrita Python, commits semânticos e tipagem.
* **`anti_patterns.md`**: Práticas proibidas no código (duplicações, IA para determinismo, constants hardcoded).
* **`architecture_principles.md`**: Diretrizes SOLID, DRY, SRP e observabilidade nativa.
* **`design_patterns.md`**: Padrões de projeto homologados (Strategy, Factory, Repository, Circuit Breaker).
* **`dependency_policy.md`**: Critérios para adição e atualização de bibliotecas.
* **`decision_protocol.md`**: O loop cognitivo de 10 passos do Observe ao Update.

### 8. `docs/runtime/` (Estado dinâmico do sistema)
* **`current_state.md`**: Sincronizado dinamicamente pelo `RuntimeCognitiveLayer` com as métricas reais do banco.
* **`active_objectives.md`**: Objetivos e metas de sprints ativas.
* **`current_blockers.md`**: Bloqueadores e severidades de execução.
* **`technical_debt.md`**: Lista de dívidas técnicas e refatorações urgentes.
* **`known_failures.md`**: Mitigação de falhas mapeadas (Playwright logins, MPT rendering timeouts).

### 9. `docs/business/` (Alinhamento comercial)
* **`business_model.md`**: Modelo de arbitragem de tráfego LTV > CPA e fases de investimento.
* **`revenue_channels.md`**: Marketing de afiliados, anúncios (AdSense) e PLR.
* **`customer_profiles.md`**: Demografia de personas-alvo (Finanças, Lifestyle, Produtividade).
* **`market_map.md`**: Tabela de taxas de CTR de baselines dos nichos de mercado.
* **`competitor_analysis.md`**: Estudo comparativo de bots rivais.

### 10. `docs/cognition/` (Cognição do fundo)
* **`beliefs.md`**: Lista de crenças estratégicas e suas confianças calibradas.
* **`hypotheses.md`**: Tabela de hipóteses estatísticas sincronizada automaticamente.
* **`assumptions.md`**: Suposições sobre restrições e punições do Pinterest.
* **`unknowns.md`**: Incógnitas de retenção algorítmica.
* **`evidence.md`**: Registro de evidências estatísticas que corroboram ou invalidam crenças.

### 11. `docs/architecture/` (Fronteiras Arquiteturais)
* **`open_source_boundary.md`**: Definição da governança e fronteira rígida entre Cognitive Kernel proprietário e ferramentas commodity open source.

### 12. `docs/validation/` (Validação e Auditoria)
* **`SPRINT_7_2_READINESS.md` [NOVO]**: Dossiê de validação técnica, dry-runs de integração e blockers identificados na Sprint 7.2.

---

## 📁 `src/` (Código Fonte)

### `src/agents/` (Agentes Cognitivos)
* **`cognition_layer.py` [NOVO]**: Módulo da Runtime Cognitive Layer. Gerencia blockers/beliefs em markdown e sincroniza dados das tabelas SQLite no `current_state.md` e `hypotheses.md`.
* **`creative_optimizer.py`**: Otimiza criativos reprovados em qualidade usando PydanticAI.
* **`video_critic.py`**: Analisa criativos recursivamente buscando falhas de rendering.
* **`revenue_strategist.py`**: CEO cognitivo que analisa relatórios estatísticos e dita alterações de ganchos.
* **`knowledge_base.py`**: Registra padrões negativos de ganchos em `patterns.json`.

### `src/memory/` (Gateway de Memória)
* **`interface.py`**: Definição abstrata do `MemoryProvider`.
* **`sqlite_memory.py`**: Provedor de memória por similaridade de tokens Jaccard local.
* **`vector_memory.py`**: Provedor com dual-write (SQLite + Qdrant) e fallback.
* **`retrieval.py`**: Orquestrador de injeção de contexto nos prompts dos agentes.

### `src/events/` (Barramento de Eventos)
* **`event_bus.py`**: Implementação do `EventBus` singleton thread-safe com persistência em SQLite.

### `src/ports/` [NOVO] (Portas Hexagonais & Registro IoC)
* **`__init__.py`**: Exporta todas as portas, enums e tipos de configuração.
* **`registry.py`**: Container IoC de registro e resolução de dependências (`ProviderRegistry`).
* **`capabilities.py` [NOVO]**: Enum str de chaves de capacidades (`Capabilities`).
* **`config.py`**: Dataclasses de configuração para todas as Portas e Adapters.
* **Interfaces (Ports)**: `MemoryPort`, `EmbeddingPort`, `EventPort`, `LLMPort`, `WorkflowPort`, `AgentPort`, `BrowserPort`, `SearchPort`, `DocumentPort`, `FeatureStorePort`, `SecretPort`, `CachePort`, `SchedulerPort`, `ObservationAdapter` [NOVO].

### `src/adapters/` [NOVO] (Adapters Técnicos Open Source)
* **`qdrant/`**: Conector e pipelines de Embeddings implementando `EmbeddingPort`.
* **`llamaindex/`**: Retriever e motor de consulta para RAG implementando `MemoryPort`.
* **`pinterest/observation_adapter.py` [NOVO]**: Adaptador que recupera e converte CanonicalMetrics do Pinterest em Observations cognitivas.

### `src/integrations/` (Integrações Específicas do Domínio)
* **`pinterest/`**: APIs de postagem, analytics e autenticação do Pinterest.

### `src/services/` [NOVO] (Serviços e Loops de Execução)
* **`experiment_runner.py`**: Máquina de estados executando o ciclo de vida dos experimentos.
* **`decision_queue.py` [NOVO]**: Fila de priorização e transição de estados dos experimentos.
* **`observation_scheduler.py` [NOVO]**: Scheduler para coletar e inserir observações empiricamente.
* **`learning_loop.py` [NOVO]**: Loop completo e automatizado conectando execução a aprendizado científico.

### `src/core/` [NOVO] (Fronteira de APIs do Cognitive Kernel)
* **`kernel.py`**: Fachada `CognitiveKernel` que coordena e unifica todos os subsistemas cognitivos via injeção/fallbacks do `ProviderRegistry`.
* **`belief_api.py`**, **`evidence_api.py`**, **`decision_api.py`**, **`memory_api.py`**, **`event_api.py`**, **`hypothesis_api.py` [NOVO]**, **`reflection_api.py` [NOVO]**, **`planning_api.py` [NOVO]**, **`strategy_api.py` [NOVO]**, **`executive_api.py` [NOVO]**, **`tool_api.py` [NOVO]**, **`skill_api.py` [NOVO]**: Fachadas controladoras que isolam bancos, memória, eventos, hipóteses, reflexões, planos, estratégias, execuções, ferramentas e habilidades de chamadas diretas de agentes.
* **`cognition/belief_service.py` [NOVO]**: Serviço do Belief Engine coordenando o pipeline Observation -> Evidence -> Belief Revision.
* **`cognition/hypothesis_service.py` [NOVO]**, **`cognition/hypothesis_repository.py` [NOVO]**: Raciocínio científico, calibração Bayesiana de confiança e persistência SQL de hipóteses propostas, validadas ou rejeitadas.
* **`cognition/reflection_service.py` [NOVO]**, **`cognition/reflection_repository.py` [NOVO]**: Análise causal, detecção de padrões repetidos de falha e extração de lições operacionais persistidas no Grafo de Evidências.
* **`cognition/planning_service.py` [NOVO]**, **`cognition/planning_repository.py` [NOVO]**: Motores de planejamento autônomo, geração de planos prioritários baseados em objetivos e integração com a Decision Queue.
* **`cognition/executive_service.py` [NOVO]**, **`cognition/executive_repository.py` [NOVO]**: Máquina de estados executável (Executive Engine), gerenciando idempotência, retries, controle de dependências entre ações e realimentação no kernel.
* **`cognition/tool_service.py` [NOVO]**, **`cognition/tool_repository.py` [NOVO]**: Sistema de capacidades (Capability & Tool Registry), permitindo descoberta de capacidades, benchmark de utilidade composta para seleção do provedor ótimo e telemetria de execução instrumentada.
* **`cognition/skill_service.py` [NOVO]**, **`cognition/skill_repository.py` [NOVO]**: Orquestrador de competências de negócio (Skill Engine) executando fluxos de capacidades declarativos com controle de retentativas e logs de telemetria.

### `src/runtime/` [NOVO] (Ciclo de Vida e Bootstrap)
* **`runtime.py`**: Orquestrador de DI, configuração e bootstrapping da aplicação.
* **`lifecycle.py`**: Health checks dos conectores de portas ativos e ganchos de shutdown.

### `src/revenue_os/analytics/` (Motor Científico Central)
* **`database.py`**: Cérebro SQLite contendo a criação e migração das tabelas do fundo.
* **`metrics_engine.py`**: Cálculos estatísticos avançados (SciPy, testes-T).
* **`capital_allocator.py`**: Divisão Bandit (70% campeões, 30% exploração).
* **`decision_engine.py`**: Triple Gate de validação estatística de variantes.
* **`time_optimizer.py`**: Amostragem Thompson para seleção de horários ótimos.

### `src/execution/` e `src/reality/` (Automação Física)
* **`publisher/pinterest_playwright.py`**: Postador determinístico local com Vision Fallback de screenshots via Gemini 2.5 Flash.
* **`queue_worker.py`**: Consumidor assíncrono de tarefas pendentes na `publication_queue`.

---

## 📁 `tests/unit/` (Validação)

* **`test_cognition_layer.py` [NOVO]**: Testes unitários da Runtime Cognitive Layer (blockers, beliefs e database sync).
* Outros testes verificando atribuição, calibração, workers e estatísticas.
