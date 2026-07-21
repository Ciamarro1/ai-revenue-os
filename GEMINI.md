# AI Revenue OS — Contexto para Agentes de IA

> [!IMPORTANT]
> Leia todos os arquivos em [docs/](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/) antes de responder qualquer solicitação. Considere esses documentos como a fonte oficial sobre identidade, arquitetura, objetivos, restrições e padrões do AI Revenue OS. Se encontrar inconsistências entre eles e o código, aponte-as antes de implementar alterações.

## Documentos Operacionais do Agente

Todos os detalhes cruciais de comportamento, arquitetura, mapas, stack e regras estão estruturados nos seguintes diretórios e arquivos:

### 1. Como o Agente Pensa (`docs/agent/`)
- **Constituição e Comportamento**: [constitution.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/agent/constitution.md)
- **Estruturas de Prompts**: [prompt_patterns.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/agent/prompt_patterns.md)
- **Papéis do Agente**: [agent_roles.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/agent/agent_roles.md)
- **Servidores MCP**: [mcp_servers.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/agent/mcp_servers.md)
- **Arquitetura & Máquina de Estados**: [architecture.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/agent/architecture.md)

### 2. O que o Projeto Sabe (`docs/knowledge/`)
- **Estrutura de Arquivos e Banco**: [project_map.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/knowledge/project_map.md)
- **Roadmap do Projeto**: [roadmap.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/knowledge/roadmap.md)
- **Glossário de Termos**: [glossary.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/knowledge/glossary.md)
- **Stack Técnica**: [tech_stack.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/knowledge/tech_stack.md)
- **Aprendizados do Repositório**: [repository_learning.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/knowledge/repository_learning.md)

### 3. Como Experimenta (`docs/experiments/`)
- **Protocolo de Experimentação**: [experimentation_protocol.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/experiments/experimentation_protocol.md)

### 4. O que foi Pesquisado (`docs/research/`)
- **Protocolo de Pesquisa**: [research_protocol.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/research/research_protocol.md)
- **Mapa de Aquisições OS**: [open_source_acquisition_map.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/research/open_source_acquisition_map.md)

### 5. Quais Decisões já foram Tomadas (`docs/adr/`)
- **Decisões de Design (ADRs)**: [decision_log.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/adr/decision_log.md)

### 6. Como Executar Processos Recorrentes (`docs/playbooks/`)
- **Playbook de Engenharia**: [engineering_playbook.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/playbooks/engineering_playbook.md)
- **Protocolo de Avaliação**: [evaluation_protocol.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/playbooks/evaluation_protocol.md)

### 7. Quais Regras de Engenharia Seguir (`docs/standards/`)
- **Diretrizes e Padrões de Código**: [coding_standards.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/standards/coding_standards.md)
- **Antipadrões de Código**: [anti_patterns.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/standards/anti_patterns.md)
- **Princípios Arquiteturais**: [architecture_principles.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/standards/architecture_principles.md)
- **Padrões de Design Homologados**: [design_patterns.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/standards/design_patterns.md)
- **Política de Dependências**: [dependency_policy.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/standards/dependency_policy.md)
- **Protocolo de Decisão**: [decision_protocol.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/standards/decision_protocol.md)

### 8. Qual o Estado de Tempo de Execução (`docs/runtime/`)
- **Estado Operacional do OS**: [current_state.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/runtime/current_state.md)
- **Objetivos de Alta Prioridade**: [active_objectives.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/runtime/active_objectives.md)
- **Bloqueadores Ativos**: [current_blockers.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/runtime/current_blockers.md)
- **Refatorações Pendentes**: [technical_debt.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/runtime/technical_debt.md)
- **Assinaturas de Falhas Conhecidas**: [known_failures.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/runtime/known_failures.md)

### 9. Qual o Alinhamento de Negócio (`docs/business/`)
- **Modelo de Negócios / Fundo**: [business_model.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/business/business_model.md)
- **Canais de Receita**: [revenue_channels.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/business/revenue_channels.md)
- **Perfis de Consumidores (Personas)**: [customer_profiles.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/business/customer_profiles.md)
- **Mapa de Mercado & Baselines**: [market_map.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/business/market_map.md)
- **Estudo de Concorrentes**: [competitor_analysis.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/business/competitor_analysis.md)

### 10. Qual a Camada Cognitiva do Fundo (`docs/cognition/`)
- **Crenças e Níveis de Confiança**: [beliefs.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/cognition/beliefs.md)
- **Hipóteses Ativas (SQLite Sync)**: [hypotheses.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/cognition/hypotheses.md)
- **Premissas Operacionais**: [assumptions.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/cognition/assumptions.md)
- **Incógnitas de Mercado**: [unknowns.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/cognition/unknowns.md)
- **Livro de Evidências Empíricas**: [evidence.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/cognition/evidence.md)

### 11. Fronteiras Arquiteturais (`docs/architecture/`)
- **Fronteira Open Source**: [open_source_boundary.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/architecture/open_source_boundary.md)
- **Diretriz Open Source First**: [open_source_first.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/architecture/open_source_first.md)

---

## Regras Invioláveis (Resumo Executivo)

1. **NUNCA** substitua lógica determinística por agentes cognitivos/LLMs para fluxos repetitivos.
2. **NUNCA** altere cálculos em `src/revenue_os/analytics/` sem rodar os testes antes E depois.
3. Toda lógica de redes sociais fica em `src/reality/` ou `src/execution/`, **NUNCA** em `analytics/`.
4. Use **Conventional Commits**: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`.
5. Mantenha a **tipagem estrita** com Pydantic em todos os schemas.
6. O `prod_db.sqlite3` é o banco de produção — **NUNCA** apague ou faça DROP.
7. Testes unitários usam `:memory:` (SQLite in-memory), nunca o banco de produção.
8. Preserve a integridade do Decision Ledger (`decisions.jsonl`) — append-only.
