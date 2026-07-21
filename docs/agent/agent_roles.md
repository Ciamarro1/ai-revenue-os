# PAPÉIS DOS AGENTES COGNITIVOS (AGENT ROLES)

Para garantir alta coesão e especialização, o AI Revenue OS define perfis cognitivos focados em responsabilidades específicas. Um único agente ou sessão de IA pode assumir papéis diferentes com base na tarefa em andamento.

---

## 1. Architect (Arquiteto)
* **Objetivo**: Garantir a consistência arquitetural de longo prazo da base de código.
* **Foco**:
  - Validar e manter a separação estrita entre as camadas (Analytics, Observability, Reality, Execution, Factory).
  - Impedir que regras de redes sociais vazem para o motor estatístico.
  - Assegurar a aplicação de padrões de design aprovados (Strategy, Factory, Circuit Breaker).

## 2. Researcher (Pesquisador)
* **Objetivo**: Adquirir conhecimento externo e contextualizar alterações.
* **Foco**:
  - Consultar APIs oficiais, RFCs e changelogs antes de programar novas integrações.
  - Investigar dependências e bugs em repositórios públicos (GitHub).
  - Usar os servidores MCP (como `context7` e `sequential-thinking`) para mapear fluxos complexos de código.

## 3. Reviewer (Revisor)
* **Objetivo**: Manter o padrão de qualidade técnica e prevenir bugs.
* **Foco**:
  - Rodar linters (Ruff) e formatadores (Black) antes de promover código.
  - Garantir a criação de testes unitários para toda lógica nova.
  - Validar o tratamento de exceções e a tipagem de dados com Pydantic v2.

## 4. Refactoring Engineer (Engenheiro de Refatoração)
* **Objetivo**: Reduzir a complexidade de código e dívidas técnicas.
* **Foco**:
  - Identificar e eliminar duplicações de código.
  - Remover código morto ou obsoleto.
  - Reduzir o acoplamento de classes e desacoplar lógica de infraestrutura.

## 5. Data Engineer (Engenheiro de Dados)
* **Objetivo**: Gerenciar a consistência relacional e otimizar queries estatísticas.
* **Foco**:
  - Validar schemas de migração do SQLite (`prod_db.sqlite3`).
  - Otimizar consultas de atribuição de receita e alocação Bandit.
  - Garantir integridade de concorrência de banco.

## 6. Growth Engineer (Engenheiro de Crescimento)
* **Objetivo**: Maximizar a atração de cliques e a geração de receita.
* **Foco**:
  - Mapear a performance de novos ganchos criativos no banco de dados.
  - Analisar métricas reais de CTR e conversão na Genome Library.
  - Refinar e recalibrar o otimizador de horários de postagem (`TimeOptimizer`).

## 7. Security Engineer (Engenheiro de Segurança)
* **Objetivo**: Mitigar riscos de infraestrutura, cookies e dados sensíveis.
* **Foco**:
  - Evitar o vazamento de segredos, cookies salvos de sessões e chaves de API nos logs.
  - Monitorar o `Trust Score` da conta e calibrar limites do `PinterestSafetyCoordinator`.
  - Garantir o correto vedamento dos logs com manifestos criptográficos SHA256.

## 8. Performance Engineer (Engenheiro de Performance)
* **Objetivo**: Otimizar tempos de processamento e uso de recursos.
* **Foco**:
  - Monitorar milissegundos gastos via `TimingContext` e MLflow.
  - Identificar gargalos de renderização de vídeo e chamadas externas de rede.
  - Otimizar o consumo de RAM e CPU nos processos Playwright em background.

## 9. Documentation Engineer (Engenheiro de Documentação)
* **Objetivo**: Garantir transparência e interpretabilidade absoluta do sistema.
* **Foco**:
  - Manter o `README.md` e o `project_map.md` sempre em sincronia com o código real.
  - Atualizar o log de decisões (ADRs) com justificativas técnicas sob mudanças críticas.
  - Garantir que o glossário reflita novos conceitos do domínio.
