# DIRETRIZES E DIRETIVAS DE ARQUITETURA (ARCHITECTURE_GUARDRAILS.md)

Este documento estabelece as regras de governança estrutural e diretrizes de conformidade de código do **AI Revenue OS**. O não cumprimento destas regras resultará em rejeição automática nas revisões de código.

---

## 🚫 1. Regras de Importação de Código (Import Restrictions)

1. **Acesso ao Domínio (Core)**:
   - Os arquivos em `src/core/` **NUNCA** podem importar de `src/adapters/`, `src/integrations/` ou `src/runtime/`.
   - Os arquivos em `src/core/` **NUNCA** podem fazer importações diretas de bibliotecas pesadas de terceiros (ex. `qdrant_client`, `temporalio`, `litellm`, `playwright`).
   - Todo acesso a capacidades físicas deve passar exclusivamente pela resolução dinâmica via `ProviderRegistry` usando interfaces abstratas de `src/ports/`.

2. **Acesso às Fachadas de Fronteira (API Boundary)**:
   - Agentes externos e motores de workflows orquestrados no LangGraph/Temporal se comunicam com a lógica do sistema exclusivamente através da fachada `CognitiveKernel` (`src/core/kernel.py`) ou suas sub-APIs (`BeliefAPI`, `EvidenceAPI`, etc.).
   - Acesso direto de agentes externos a tabelas do banco de dados SQLite (`src/revenue_os/analytics/database.py`) ou bancos de vetores é estritamente proibido.

3. **Independência das Portas**:
   - Os arquivos sob `src/ports/` contêm apenas interfaces abstratas e configurações de tipo primitivas. Eles **NUNCA** importam lógica ou adaptadores concretos.

---

## 🤝 2. Diretrizes para Contribuição e Extensão

1. **Novo Provider / Adaptador**:
   - Deve estender uma interface abstrata (Port) existente.
   - Deve ser registrado no bootstrapping da aplicação em `src/runtime/runtime.py` via `ProviderRegistry`.
   - Parâmetros físicos de conexão (host, port, token) devem ser injetados exclusivamente pelas dataclasses correspondentes em `src/ports/config.py`.

2. **Mapeamento de Capacidade**:
   - Qualquer nova capacidade introduzida no ecossistema deve primeiro ser declarada no Enum `Capabilities` (`src/ports/capabilities.py`) antes de ser registrada ou resolvida.

3. **Modificações Estruturais**:
   - Nenhuma alteração estrutural nas portas, interfaces ou modelo hexagonal pode ocorrer sem o registro prévio de um novo relatório de decisão arquitetural (**ADR**) em `docs/adr/decision_log.md`.

---

## 🧪 3. Conformidade e Qualidade nos Testes

1. **Isolamento e Limpeza**:
   - Todos os testes unitários que utilizam o `ProviderRegistry` ou `EventBus` singleton devem invocar `.clear()` e `.clear_listeners()` nos setups/teardowns para garantir isolamento absoluto entre casos de teste.
   - Testes unitários devem usar `:memory:` (bancos em memória temporários), impedindo qualquer alteração ou poluição de dados no banco de produção local (`prod_db.sqlite3`).
