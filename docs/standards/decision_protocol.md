# PROTOCOLO DE TOMADA DE DECISÃO (DECISION PROTOCOL)

Todo ciclo de melhoria, correção ou evolução arquitetural no AI Revenue OS deve seguir rigorosamente o loop cognitivo estruturado em 10 etapas consecutivas.

---

## O Loop de Tomada de Decisão

```text
  Observe ➔ Pesquisar ➔ Planejar ➔ Comparar ➔ Implementar
                                                 │
  Atualizar ⮘ Aprender ⮘ Medir ⮘ Documentar ⮘ Testar
```

### 1. Observe (Observar)
- Identificar falhas em logs estruturados, alertas de disjuntor (AUTOPAUSE), desvios temporais de métricas, solicitações do usuário ou bugs de execução de rede.

### 2. Pesquisar (Investigar)
- Varrer a base de código correspondente, investigar APIs oficiais, issues do GitHub, changelogs e consultar informações via servidores MCP (`context7`, `sqlite`).

### 3. Planejar (Planejar)
- Desenhar a solução arquitetural por escrito. Criar um plano de implementação (`implementation_plan.md`) detalhando arquivos a modificar, novos arquivos a criar e a suite de testes de validação.

### 4. Comparar (Avaliar Alternativas)
- Avaliar diferentes abordagens com base nos 6 pilares de engenharia (Complexidade, Escalabilidade, Manutenção, Custo, Observabilidade, Risco). Selecionar o caminho mais robusto no longo prazo.

### 5. Implementar (Codificar)
- Escrever código limpo, modular, injetável, com tipagem estrita via Pydantic v2, seguindo os padrões de design definidos e evitando antipadrões de código.

### 6. Testar (Validar)
- Executar a suite de testes locais (`pytest`) para garantir a ausência de regressões técnicas. Escrever novos casos de teste para validar o código implementado.

### 7. Documentar (Registrar)
- Atualizar a documentação técnica relevante, o log de decisões (ADR) se a mudança for arquitetural e o mapa do repositório se novos arquivos forem adicionados.

### 8. Medir (Avaliar Resultados)
- Monitorar a performance pós-deploy utilizando logs do `TimingContext`, dados do MLflow e checando a calibragem de métricas e estabilidade de conexões físicas.

### 9. Aprender (Consolidar Descobertas)
- Analisar falhas ou comportamentos inesperados observados na execução prática do novo código (ex: timeouts em determinados horários ou instabilidade de cookies).

### 10. Atualizar Conhecimento (Persistir Aprendizado)
- Gravar as descobertas no arquivo [repository_learning.md](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/docs/knowledge/repository_learning.md) para que futuras sessões de agentes de IA utilizem esse aprendizado acumulado automaticamente, evitando repetir erros passados.
