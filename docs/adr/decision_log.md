# LOG DE DECISÕES ARQUITETURAIS (ADR)

Este arquivo documenta as principais decisões de design técnico tomadas na evolução da arquitetura do AI Revenue OS.

---

## ADR 001: Desacoplamento da Execução da Inteligência
* **Status**: Aprovado e Implementado
* **Contexto**: Anteriormente, o runner dependia de agentes cognitivos baseados em LLMs (como OpenManus e Aiden) para realizar o upload físico e navegação no Pinterest. Isso gerava alta latência, custos elevados com APIs e timeouts recorrentes na postagem.
* **Decisão**: Criou-se a Execution Layer. A inteligência decide o que publicar através de experimentos agendados na tabela SQLite `publication_queue`. O `QueueWorker` consome a fila em background de forma determinística utilizando scripts locais baseados em Playwright.
* **Impacto**: Redução drástica de falhas e consumo de tokens LLM em postagens rotineiras.

---

## ADR 002: Inclusão de Vision Fallback
* **Status**: Aprovado e Implementado
* **Contexto**: A publicação via Playwright determinístico quebra quando o layout do Pinterest é atualizado pela plataforma, quebrando seletores CSS ou XPath pré-mapeados.
* **Decisão**: Implementar um mecanismo de auto-recuperação cognitivo (`Vision Fallback`). Quando o Playwright não localiza um botão, tira um screenshot da viewport (fixada em 1280x800) e envia para a API do OpenRouter (`google/gemini-2.5-flash`). O modelo retorna seletores textuais ou coordenadas `(x, y)` corretas para realizar o clique na tela.
* **Impacto**: Resiliência do robô de atuação física contra mudanças de layout do site.

---

## ADR 003: Disjuntor Geral (AUTOPAUSE Circuit Breaker)
* **Status**: Aprovado e Implementado
* **Contexto**: Em execuções 100% autônomas, erros de concorrência de escrita, falta de espaço em disco, vazamento de memória ou perda de integridade dos arquivos podem quebrar o banco de produção ou corromper dados históricos.
* **Decisão**: Implementar o monitoramento de saúde do sistema (`Health Score`). Caso a saúde geral caia abaixo de 90.0 ou seja detectada uma anomalia física grave, a flag global `AUTOPAUSE` é gravada no SQLite. Todos os workers de execução e loops de postagem consultam essa flag antes de agir, travando imediatamente todas as publicações externas.
* **Impacto**: Proteção do caixa do fundo e da reputação da conta em situações de emergência de infraestrutura.

---

## ADR 004: Anti-repetição de Criativos via Hash Perceptual (Deduplication)
* **Status**: Aprovado e Implementado
* **Contexto**: IA gerando imagens visualmente idênticas sob prompts de exploração semelhantes. Postar criativos redundantes degrada a relevância da conta no Pinterest e ativa alarmes de spam das redes.
* **Decisão**: Criar o `ImageDeduplicator` na camada de qualidade (`src/factory/quality/image_dedup.py`). O sistema calcula hashes perceptuais (pHash, aHash, dHash) com a biblioteca `imagehash` e impede a publicação se a distância de Hamming com imagens do histórico recente for menor ou igual a 10.
* **Impacto**: Filtragem pré-postagem contra spam visual.

---

## ADR 005: Runtime Cognitive Layer (Camada Cognitiva de Tempo de Execução)
* **Status**: Aprovado e Implementado
* **Contexto**: Agentes cognitivos autônomos precisam acessar de forma unificada e de maneira bidirecional o estado atual do sistema, os bloqueadores operacionais ativos, crenças calibradas e hipóteses científicas de mercado sem depender de parsing de strings manual ad-hoc ou chamadas desnecessárias de LLM.
* **Decisão**: Implementar o módulo `RuntimeCognitiveLayer` em `src/agents/cognition_layer.py`. Ele mapeia e sincroniza dados analíticos reais do banco SQLite (`ExperimentDatabase`) diretamente para os arquivos markdown em `/docs/runtime/` e `/docs/cognition/`, além de expor interfaces limpas em Python para gerenciamento de bloqueadores e crenças.
* **Impacto**: Sincronização automatizada e bidirecional de documentações operacionais de tempo de execução, fornecendo contexto estruturado atualizado para qualquer agente autônomo.

---

## ADR 006: Cognitive Database Layer (Camada de Banco de Dados Cognitivo)
* **Status**: Aprovado e Implementado
* **Contexto**: No final da Sprint 1, a memória cognitiva residia apenas em arquivos markdown locais. Para dotar o sistema de uma memória relacional estável e permitir queries de juntção SQL entre dados de testes e aprendizados acumulados, é necessária a persistência estruturada de crenças, evidências e aprendizados em banco.
* **Decisão**: Integrar tabelas cognitivas (`beliefs`, `evidence`, `learnings`) diretamente no banco de dados SQLite unificado `prod_db.sqlite3`. A gravação é controlada por uma classe repositório `CognitiveRepository` que atualiza síncrona e imediatamente os Markdowns associados. O preenchimento da evidência é híbrido (a estatística é determinística e a narrativa é enriquecida cognitivamente pelo agente).
* **Impacto**: Persistência de memória estável e indexada no banco de dados relacional, mantendo a documentação sincronizada síncrona e automaticamente.

---

## ADR 007: Belief Evolution Engine (Motor de Evolução de Crenças)
* **Status**: Aprovado e Implementado
* **Contexto**: Com as crenças e evidências persistidas relacionalmente no final da Sprint 2, falta um motor matemático de aprendizado capaz de recalibrar as confianças das crenças dinamicamente à medida que evidências de novos experimentos são registradas, salvando a trajetória dessas confianças.
* **Decisão**: Implementar a tabela `belief_history` no SQLite para armazenar as mudanças históricas de confiança e criar o `BeliefManager` em `src/cognition/belief_manager.py` aplicando fórmulas de atualização baseadas no impacto e nível de confiança da evidência, atualizando os Markdowns de forma síncrona com os logs históricos detalhados.
* **Impacto**: Habilidade do sistema de aprender de forma cumulativa com campanhas anteriores, gerando uma trajetória histórica de evolução de suas crenças.

---

## ADR 008: Evidence Intelligence Engine (Motor de Inteligência de Evidências)
* **Status**: Aprovado e Implementado
* **Contexto**: No final da Sprint 3, a atualização de confiança de crenças ocorria de forma cega, ponderando todas as evidências com o mesmo peso. Contudo, experimentos com amostras microscópicas ou fontes não confiáveis devem influenciar menos a evolução de crenças estratégicas do que experimentos robustos.
* **Decisão**: Criar a tabela `evidence_quality` e implementar a classe `EvidenceEngine` em `src/cognition/evidence_engine.py` para calcular um escore de qualidade agregador (baseado em tamanho de amostra logarítmico, significância estatística, recência temporal e confiabilidade da fonte). Integrar esse escore como um multiplicador ponderador na fórmula de atualização do `BeliefManager`.
* **Impacto**: Estabilização do aprendizado cognitivo do sistema mitigando oscilações causadas por ruídos experimentais e dados pouco significativos.

---

## ADR 009: Integração de Componentes Open Source Consolidados (Membros do Sistema)
* **Status**: Aprovado e Implementado
* **Contexto**: Para expandir o AI Revenue OS nas próximas sprints de forma ágil e evitar o retrabalho de construir ferramentas de orquestração de infraestrutura do zero (multi-agentes, workflows distribuídos, filas de tarefas, analítica comportamental, vector data), precisamos desenhar uma fronteira clara entre o que é código cognitivo proprietário (Cérebro) e o que é de mercado (Membros).
* **Decisão**: Adotar oficialmente projetos open-source maduros nas próximas sprints:
  - Roteamento de agentes cíclicos com estado: **LangGraph**.
  - Orquestrador de workflows experimentais longos: **Temporal.io**.
  - Automação física e postagens sociais: **n8n**.
  - Coleta de dados e analítica em tempo real: **PostHog**.
  - Armazenamento de embeddings semânticos: **Qdrant**.
* **Impacto**: Aceleração dramática na entrega das próximas fases, focando todo o esforço de engenharia do time no desenvolvimento do Cognitive Kernel proprietário.

---

## ADR 010: Alinhamento de Roadmap e Priorização de Camada Vetorial (Sprint 5)
* **Status**: Aprovado e Implementado
* **Contexto**: Com o núcleo epistemológico estruturado de Sprints 1–4 concluído, precisamos definir a próxima sprint de execução lógica. Em vez de iniciar imediatamente o roteamento de múltiplos agentes (LangGraph), é prioritário munir o sistema de uma memória semântica indexada de longo prazo para buscar qualitativamente o histórico de aprendizados passados e notas de concorrência.
* **Decisão**: Refinar a ordem cronológica do Roadmap Operacional, elegendo a **Sprint 5: Memory & Retrieval Layer** (Qdrant + LlamaIndex) como a prioridade imediata de desenvolvimento de infraestrutura.
* **Impacto**: Garante que o conselho de agentes (LangGraph, Sprint 6) já inicialize consumindo uma base de memória semântica robusta e contextualizada.

---

## ADR 011: Memory & Retrieval Layer (Camada de Memória e Recuperação Semântica)
* **Status**: Aprovado e Implementado
* **Contexto**: Para suportar a recuperação qualitativa semântica de aprendizados anteriores de forma desacoplada de fornecedores específicos de bancos vetoriais, precisamos de uma arquitetura de gateway de memória abstrata.
* **Decisão**: Criar a interface abstrata `MemoryProvider` no diretório `src/memory/` e implementar duas especializações: `SQLiteMemoryProvider` (que fornece busca por similaridade de tokens baseada em Jaccard localmente, ideal para testes unitários estáveis e rápidos out-of-the-box) e `VectorMemoryProvider` (que encapsula futuras conexões Qdrant e LlamaIndex, executando um fallback resiliente e transparente para o SQLite local caso as APIs estejam offline).
* **Impacto**: Garantia de desacoplamento entre o núcleo de decisão cognitivo proprietário e a tecnologia física de armazenamento vetorial, promovendo testes robustos e autônomos sem dependências pesadas de infraestrutura.

---

## ADR 012: Open Source Integration Hardening (Endurecimento das Integrações Open Source)
* **Status**: Aprovado e Implementado
* **Contexto**: Os adapters de Qdrant e LlamaIndex criados na Sprint 5 eram stubs vazios (placeholders). Para que os agentes possam acumular inteligência semântica real antes da Sprint 6 (LangGraph), é necessário substituir esses stubs por adapters de produção com: conexão real ao Qdrant via Docker, pipeline de embeddings (sentence-transformers com fallback hash), gerenciador de coleções vetoriais, retriever semântico e motor de consulta contextual.
* **Decisão**: Reescrever completamente os pacotes `src/integrations/qdrant/` e `src/integrations/llamaindex/` com implementações de produção. Adotar arquitetura de dual-write no `VectorMemoryProvider` (SQLite sempre + Qdrant quando disponível). Todas as dependências externas (qdrant-client, sentence-transformers) sono opcionais — importadas via try/except e declaradas no grupo `[vector]` do `pyproject.toml`. Corrigir o bug de classe duplicada em `vector_memory.py`. Adicionar serviço Qdrant ao `docker-compose.yml`.
* **Impacto**: O sistema agora possui uma pipeline de embeddings funcional e uma camada de busca semântica real, mantendo 100% de compatibilidade com ambientes sem Docker/GPU graças ao fallback SQLite + hash vectorizer.

---

## ADR 013: Governança e Fronteira de Desenvolvimento Open Source
* **Status**: Aprovado e Implementado
* **Contexto**: A evolução rápida do AI Revenue OS nas próximas sprints de inteligência artificial de agentes e fluxos de longa duração exige a definição de limites rígidos sobre quais partes do código constituem propriedade intelectual científica (Cognitive Kernel) e quais são tratadas como commodities adaptadoras (Integration Layer).
* **Decisão**: Criar o documento `docs/architecture/open_source_boundary.md` e estabelecer que os módulos centrais (Beliefs, Evidence, Decisions, Revenue discovery) permanecem 100% livres de dependências diretas de bibliotecas externas (com imports permitidos apenas via wrappers e interfaces de gateways). Alinhar a ordem cronológica das Sprints 6 a 10 de acordo com as necessidades operacionais e observabilidade dos agentes.
* **Impacto**: Prevenção de acoplamento indesejado no core cognitivo e aumento da manutenibilidade do ecossistema a longo prazo.

---

## ADR 014: Cognitive Event Bus (Barramento de Eventos Cognitivos)
* **Status**: Aprovado e Implementado
* **Contexto**: Para suportar a comunicação desacoplada entre os componentes do Cognitive Kernel (crenças, evidências) e permitir que futuros orquestradores (como o LangGraph ou Temporal) reajam a eventos de forma assíncrona, precisamos de um barramento de eventos unificado.
* **Decisão**: Criar o módulo `EventBus` em `src/events/event_bus.py` utilizando um padrão singleton thread-safe. Persistir todos os eventos publicados na tabela `cognitive_events` do SQLite para fins de rastreabilidade histórica completa. Integrar ganchos automáticos de publicação de eventos em mutações do `BeliefManager` (`BeliefUpdated`) e `EvidenceEngine` (`EvidenceEvaluated`).
* **Impacto**: Desacoplamento de fluxos operacionais, permitindo auditorias de traces retroativas em logs e integração simplificada com barramentos open source no futuro.

---

## ADR 015: Cognitive Kernel API Boundary (Fronteira de APIs do Kernel)
* **Status**: Aprovado e Implementado
* **Contexto**: Para suportar a chegada de agentes LangGraph de forma desacoplada e segura, precisamos impedir que os agentes acessem diretamente as tabelas do banco de dados, provedores vetoriais ou chamem lógicas de evolução ad-hoc.
* **Decisão**: Criar o pacote `src/kernel/` contendo as fachadas de fronteira (`BeliefAPI`, `EvidenceAPI`, `DecisionAPI`, `MemoryAPI`, `EventAPI`) coordenadas pelo master orchestrator `CognitiveKernel` para unificar e encapsular todos os subsistemas cognitivos.
* **Impacto**: Garantia de isolamento e governança de dados, forçando todos os acessos dos agentes a passarem pela API segura do Kernel.

---

## ADR 016: Unified Open Source Acquisition & Provider Boundary Strategy
* **Status**: Aprovado e Implementado
* **Contexto**: Para consolidar a arquitetura com o máximo de retorno operacional sem reinventar a roda, é preciso desenhar a governança de integrações open-source avançadas (como orquestradores cíclicos de agentes, orquestradores de transações longas, feature stores, grafos relacionais e telemetria distribuída).
* **Decisão**: Atualizar as diretrizes em `open_source_boundary.md` e `open_source_acquisition_map.md` definindo a arquitetura em 4 camadas (Interfaces, Kernel, Open Source, Providers). Estabelecer o uso do LangGraph como runtime completo do conselho de agentes, Temporal/Prefect para workflows, Feast como Feature Store, Neo4j para relações causais, e a stack Grafana para observabilidade distribuída. Realign Sprints 6-10.
* **Impacto**: Garantia de uma infraestrutura robusta, escalável e de fácil manutenção, focando os recursos proprietários na evolução científica do Cognitive Kernel.

---

## ADR 017: Hexagonal Ports & Adapters Architecture Freeze (Congelamento Arquitetural)
* **Status**: Aprovado e Implementado
* **Contexto**: Para consolidar a estabilidade do sistema antes da Sprint 6, precisamos proteger o Cognitive Kernel contra dependências acopladas de frameworks de terceiros por meio de Portas (`ports`) abstratas.
* **Decisão**: Criar as interfaces abstratas `MemoryPort`, `EmbeddingPort`, `EventPort`, `LLMPort`, `WorkflowPort`, `AgentPort`, `BrowserPort`, `SearchPort`, `DocumentPort` e `FeatureStorePort` sob `src/ports/` e fazer com que os adapters implementem essas portas.
* **Impacto**: Isolamento absoluto do kernel contra mudanças em bibliotecas de terceiros.

---

## ADR 018: Hexagonal Restructuring & IoC Provider Registry
* **Status**: Aprovado e Implementado
* **Contexto**: O kernel não deve importar adaptadores concretos diretamente. Para evitar dependências estáticas, precisamos de um mecanismo dinâmico de Inversão de Controle (IoC) e Capabilities.
* **Decisão**: Criar o `ProviderRegistry` sob `src/ports/registry.py` atuando como container IoC thread-safe. Mover as portas para `src/ports/`, adaptadores gerais para `src/adapters/` e integrações de negócio para `src/integrations/`. Introduzir `src/ports/config.py` para gerenciamento centralizado de configurações de portas.
* **Impacto**: Flexibilidade extrema para substituir qualquer adaptador sem tocar em uma única linha de código do cérebro cognitivo.

---

## ADR 019: Runtime Lifecycle and Capability-based Decoupling
* **Status**: Aprovado e Implementado
* **Contexto**: Para suportar a complexidade operacional da aplicação, precisamos desacoplar as responsabilidades de bootstrap, injeção de dependências e health checks da inteligência principal.
* **Decisão**: Criar o namespace `src/runtime/` contendo `runtime.py` e `lifecycle.py` para isolar a orquestração do ciclo de vida, bootstrapping de conexões e verificação de saúde operacional. Mover `src/kernel/` para `src/core/`.
* **Impacto**: Organização modular de nível corporativo, mantendo a inteligência de negócios do Kernel pautada no domínio puro.

---

## ADR 020: Capabilities Enum & Manifest Loader (Manifesto de Capacidades)
* **Status**: Aprovado e Implementado
* **Contexto**: Para evitar erros tipográficos em strings de capacidades de IoC e permitir alterar adaptadores de infraestrutura sob demanda sem alterar código, precisamos de chaves fortemente tipadas e um manifesto de configuração dinâmico.
* **Decisão**: Criar o módulo `Capabilities` como um str-enum sob `src/ports/capabilities.py`. Refatorar `ProviderRegistry` para aceitar chaves `Capabilities`. Desenvolver o carregador dinâmico de manifesto em `KernelConfig.load_manifest()` buscando por `capability_manifest.json` no diretório raiz.
* **Impacto**: Configuração de capacidades centralizada e acoplamento extremamente flexível conduzido por arquivos declarativos de configuração manifest.

---

## ADR 021: Final Directory Cleanups (Consolidação do Core)
* **Status**: Aprovado e Implementado
* **Contexto**: Para consolidar a Arquitetura Hexagonal estrita, todas as implementações e namespaces de domínio (memory, events, cognition) que estavam na raiz do projeto devem ser movidos para dentro de `src/core/`.
* **Decisão**: Mover `src/memory/` para `src/core/memory/`, `src/events/` para `src/core/events/` e `src/cognition/` para `src/core/cognition/`. Atualizar todos os imports correspondentes.
* **Impacto**: Organização de domínio 100% isolada e limpa no pacote `src/core/`.

---

## ADR 022: Final Hexagonal Architecture Freeze & Documentation
* **Status**: Aprovado e Implementado
* **Contexto**: Para garantir que as futuras fases de integração técnica e inteligência de negócios não poluam a pureza do domínio de negócios do Core com dependências de terceiros, precisamos documentar formalmente e congelar as regras de governança estrutural.
* **Decisão**: Criar `ARCHITECTURE.md`, `CAPABILITIES.md` e `PROVIDER_MANIFEST.md` sob `docs/architecture/` documentando o fluxo de dependências, catálogo de capacidades e guias de novos provedores. Congelar formalmente as regras de injeção de dependências.
* **Impacto**: Estabelecimento de barreiras de governança e disciplina arquitetural definitivas para o crescimento saudável da plataforma.

---

## ADR 023: Architecture Guardrails & Governance
* **Status**: Aprovado e Implementado
* **Contexto**: Com a plataforma estabilizada e a arquitetura hexagonal concluída, precisamos estabelecer barreiras de governança objetivas para impedir a degradação de dependências conforme novas implementações e frameworks são adicionados.
* **Decisão**: Criar o manual `ARCHITECTURE_GUARDRAILS.md` sob `docs/architecture/` contendo regras e limites estritos sobre a pureza das dependências do `core/`, isolamento do banco e governança nas revisões de código.
* **Impacto**: Garantia de disciplina arquitetural perpétua, mantendo o domínio de negócios 100% livre de acoplamentos tecnológicos.

---

## ADR 024: Belief Engine Implementation (Cognitive Kernel)
* **Status**: Aprovado e Implementado
* **Contexto**: Para iniciar a Fase 6 focada em inteligência agêntica, o sistema precisa de um motor de raciocínio empírico estruturado (Belief Engine) capaz de coletar fatos observados, sintetizar evidências empíricas e refinar premissas estratégicas acumuladas (crenças).
* **Decisão**: Criar o modelo `Observation` em `models.py`. Desenvolver a persistência e mapeamento de observações no banco SQLite. Implementar o `BeliefService` coordenando o pipeline `Observation -> Evidence -> Belief -> Confidence -> Revision`.
* **Impacto**: Primeira capacidade cognitiva funcional implementada de forma desacoplada e 100% testada.

---

## ADR 025: Evidence Graph Implementation
* **Status**: Aprovado e Implementado
* **Contexto**: Para tornar os rastros de raciocínio cognitivo auditáveis, necessitamos de mapear dependências e caminhos não lineares entre observações, evidências, crenças, experimentos e decisões.
* **Decisão**: Criar tabelas `cognitive_graph_nodes` e `cognitive_graph_edges` no SQLite e implementar algoritmos de busca (DFS/BFS reversos) no repositório para responder a trace queries ("quais observações originaram crença X", etc.).
* **Impacto**: Completa rastreabilidade e explicabilidade das conexões cognitivas no ecossistema.

---

## ADR 026: Hypothesis Engine Implementation
* **Status**: Aprovado e Implementado
* **Contexto**: Para que o AI Revenue OS conduza investigações científicas autônomas, ele necessita formular hipóteses causais, calibrar sua confiança com base em nova evidência estatística e promovê-las para experimentos ativos.
* **Decisão**: Definir o modelo `Hypothesis`, criar a persistência `HypothesisRepository`, a lógica de calibração Bayesiana em `HypothesisService`, e integrar as dependências causais no Grafo de Evidências, gerando experimentos vinculados ao banco relacional do laboratório.
* **Impacto**: Capacidade de raciocínio causal integrado, permitindo que a camada agêntica formule e teste hipóteses cientificamente.

---

## ADR 027: Revenue Scientist Loop Integration
* **Status**: Aprovado e Implementado
* **Contexto**: Para fechar o ciclo de aprendizado com dados reais de negócio e gerar receita de forma autônoma e científica, precisamos conectar a criação, execução, medição e refatoração estatística em um loop de feedback contínuo (learning loop).
* **Decisão**: Implementar a porta `ObservationAdapter`, criar o adaptador do Pinterest, desenvolver o `ObservationScheduler` para ingerir métricas, criar a fila de decisão `DecisionQueue` para priorização e gerenciar o ciclo de vida dos experimentos (Pending -> Running -> Completed -> Failed) sob o orquestrador central `LearningLoop`.
* **Impacto**: Ciclo de aprendizado empírico fechado, permitindo que o sistema aprenda continuamente a partir dos dados reais de performance do Pinterest de forma autônoma.

---

## ADR 028: Reflection Engine (Self-Reflective Loops)
* **Status**: Aprovado e Implementado
* **Contexto**: Para que o AI Revenue OS compreenda e explique por que determinados experimentos obtiveram sucesso ou falharam, ele necessita de uma camada de reflexão pós-experimento que identifique causas raiz, agrupe padrões históricos e extraia lições de longo prazo.
* **Decisão**: Implementar os modelos `Reflection` e `Lesson`. Criar a persistência SQL `ReflectionRepository` e o serviço orquestrador `ReflectionService` unindo o `RootCauseAnalyzer`, `FailurePatternDetector` e `LessonExtractor`. Conectar as reflexões e lições de volta no Grafo de Evidências, gerando nós e arestas de rastreabilidade causal (`explains`, `analyzes`, `produces`, `refines`).
* **Impacto**: O AI Revenue OS passa a entender o próprio aprendizado, enriquecendo o motor com explicação Bayesiana de desvios e orientando futuras formulações de hipóteses de forma lógica.

---

## ADR 029: Planning Engine (Empirical Strategy Plans)
* **Status**: Aprovado e Implementado
* **Contexto**: Para que o AI Revenue OS planeje de forma proativa as suas ações experimentais futuras com base no conhecimento acumulado (beliefs, hypotheses, lessons, reflections), necessitamos de um motor de planejamento estruturado.
* **Decisão**: Criar modelos de domínio `Objective`, `Plan` e `PlanStep` e persisti-los no SQLite via `PlanningRepository`. Implementar o `PlanningService` para formular planos táticos com escores de priorização que integram a confiança da hipótese à gravidade das lições aprendidas, mapeando a rastreabilidade causal (`objective -> hypothesis -> plan -> plan_step -> experiment`) e integrando à `DecisionQueue`.
* **Impacto**: O sistema passa a projetar estrategicamente o próximo experimento ideal de forma autônoma e guiada por objetivos.

---

## ADR 030: Strategy Engine (Goal-Driven Utility Optimization)
* **Status**: Aprovado e Implementado
* **Contexto**: Para permitir que o Cognitive Kernel formule objetivos estratégicos de longo prazo ordenados por valor e viabilidade em vez de planos estanques, precisamos de um resolvedor de otimização multi-objetivo.
* **Decisão**: Criar modelos de domínio `Goal`, `Strategy`, `Constraint` e `Opportunity` no SQLite. Desenvolver o `StrategyService` maximizando utilidade de receita, aprendizado, confiança e ganho de informação contra riscos, custos e restrições operacionais vigentes. Integrar no Grafo e gerar planos no Planning Engine de forma automática.
* **Impacto**: Decisão estratégica global otimizada visando o máximo retorno em aprendizado e receita.

---

## ADR 031: Executive Engine (Workflow Automation & State Machine)
* **Status**: Aprovado e Implementado
* **Contexto**: Para habilitar o AI Revenue OS a agir de forma autônoma e concretizar as estratégias selecionadas, precisamos transformar os planos abstratos em fluxos de execução transacionais robustos.
* **Decisão**: Implementar modelos `Action`, `ActionDependency` e `ExecutionHistory`. Criar o `ExecutiveService` atuando como uma máquina de estados idempotente com suporte a árvores de dependência, limites de retentativas (retries), pausas e cancelamentos. Realimentar o cérebro cognitivo emitindo novas observações e mantendo a rastreabilidade causal completa no Evidence Graph.
* **Impacto**: Automação transacional robusta e desacoplada de provedores externos, transformando planos em ações e fechando o ciclo de aprendizado.

---

## ADR 032: Capability & Tool Registry System
* **Status**: Aprovado e Implementado
* **Contexto**: Para suportar uma infinidade de provedores de IA e ferramentas (Pinterest, YouTube, Flux, ComfyUI, etc.) sem acoplar a lógica de execução (Executive Engine), precisamos de um sistema de capacidades desacoplado que permita a escolha baseada em desempenho e custo.
* **Decisão**: Desenvolver o Capability System, composto pelas tabelas `providers`, `tools`, `capabilities` e `tool_executions`. Criar o `ToolRegistryService` implementando a orquestração e seleção multi-objetivo do provedor ideal através de uma fórmula composta de utilidade de desempenho (confiabilidade, latência, custo e saúde física), atualizada de forma rolante a cada execução. Mapear toda a árvore causal no Evidence Graph (`implements`, `provided_by`, `runs`, `invokes`).
* **Impacto**: Desacoplamento absoluto entre o cérebro cognitivo de tomada de decisão e os agentes/serviços de infraestrutura de postagem e geração de mídia.

---

## ADR 033: Skill Engine (Operational Workflows & Orchestration)
* **Status**: Aprovado e Implementado
* **Contexto**: Para traduzir planos complexos do Cognitive Kernel em competências operacionais reutilizáveis (workflows) compostas por sequências de etapas instrumentadas em ferramentas, precisamos de uma camada declarativa fina acima do Capability Registry.
* **Decisão**: Implementar tabelas SQLite `skills`, `skill_steps`, `skill_executions` e `skill_step_executions` e os respectivos modelos Pydantic. Desenvolver o `SkillRegistryService` orquestrando a injeção dinâmica de handlers executáveis, resolução dinâmica de ferramentas ótimas, execução monitorada (telemetria de latência, status de sucesso, e decaimento de confiabilidade/saúde das ferramentas executadas), regras de retentativas (retry policies) e publicação de eventos de tempo de execução (`SkillStarted`, `SkillStepCompleted`, `SkillCompleted`, `SkillFailed`) através do barramento `EventBus`.
* **Impacto**: Capacitação declarativa flexível e desacoplada que fornece as primeiras 5 habilidades operacionais necessárias para o teste de loop de ponta a ponta na Sprint 7.5.







