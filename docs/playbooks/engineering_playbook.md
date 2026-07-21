# PLAYBOOK DE ENGENHARIA (ENGINEERING PLAYBOOK)

Este documento define os princípios de tomada de decisão técnica aplicados por engenheiros e agentes cognitivos ao projetar ou modificar o AI Revenue OS.

---

## 1. Fluxo de Decisão Sob Múltiplas Soluções

Quando existir mais de uma alternativa técnica para resolver um problema, avalie e quantifique cada uma delas seguindo os 6 pilares de engenharia:

### P1. Medir Complexidade
- Priorize a solução com o menor número de linhas de código, menos níveis de aninhamento (nesting) e menor complexidade ciclomática.
- Evite abstrações precoces. Aplique o princípio DRY (Don't Repeat Yourself), mas lembre-se: a duplicação de código é preferível a abstrações incorretas ou confusas.

### P2. Medir Escalabilidade
- Como a solução se comporta sob alto volume de dados (ex: milhões de linhas de métricas no SQLite ou posts agendados na fila)?
- Há risco de gargalo de concorrência ou concorrência de escrita no SQLite? Se sim, utilize transações estruturadas.

### P3. Medir Manutenção
- O código escrito é fácil de ser compreendido por outro agente de IA ou desenvolvedor humano no futuro?
- Existem testes robustos cobrindo os caminhos críticos e de falha?
- A tipagem Pydantic está clara e bem estruturada?

### P4. Medir Custo
- Qual é o custo financeiro real da solução?
- Minimizar chamadas desnecessárias de APIs de modelos de Linguagem de grande porte (LLMs).
- Otimizar o tempo de execução do Playwright no navegador para economizar custos de processamento (CPU/GPU).

### P5. Medir Observabilidade
- A solução possui logs estruturados que permitem depurar falhas em produção silenciosa?
- Os tempos de execução de etapas externas críticas estão instrumentados com o `TimingContext` e exportados para o MLflow ou OpenTelemetry?

### P6. Medir Risco
- Qual o risco de a alteração quebrar outros módulos integrados (Analytics, Adapters, Execution)?
- A automação tem risco de violar políticas de spam das redes sociais (reduzindo o Trust Score)?
- Há risco de vazamento de credenciais ou chaves de API?

---

## 2. Critérios de Escolha e Justificativa

* **Proibido "Fast over Safe"**: **Nunca** selecione uma solução apenas porque é mais rápida ou fácil de implementar de imediato se ela comprometer qualquer um dos pilares acima.
* **Justificativa Explicita**: No log de decisões (ADR) ou na descrição de commits semânticos, justifique claramente a escolha técnica com base nas métricas avaliadas dos 6 pilares de engenharia.
