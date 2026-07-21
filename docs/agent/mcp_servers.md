# SERVIDORES MCP (MODEL CONTEXT PROTOCOL)

O AI Revenue OS disponibiliza ferramentas cognitivas estruturadas via servidores MCP para permitir que os agentes interajam de forma segura com o ambiente de desenvolvimento.

---

## Inventário de Servidores MCP e Ferramentas

### 1. `sqlite`
* **Descrição**: Conector direto para o banco de dados.
* **Ferramentas**: `query`, `execute`, `describe-table`, `list-tables`, `transaction`.
* **Quando Usar**:
  - Investigar o estado atual das hipóteses, experimentos ou fila de publicação.
  - Verificar valores de métricas observadas ou conferir se a flag de `AUTOPAUSE` está ativa.
* **Restrição**: **NUNCA** execute comandos de alteração estrutural (`DROP`, `DELETE`) no banco de produção sem auditoria de testes prévia.

### 2. `playwright`
* **Descrição**: Automação de navegador para depuração visual e testes interativos.
* **Ferramentas**: `browser_navigate`, `browser_click`, `browser_type`, `browser_take_screenshot`, `browser_fill_form`, etc.
* **Quando Usar**:
  - Testar fluxos de publicação interativamente.
  - Capturar screenshots de telas sob falhas de seletores para alimentar o Vision Fallback.
* **Restrição**: Não utilize para tarefas repetitivas em produção autónoma (estas devem ser executadas pelo `QueueWorker` determinístico).

### 3. `context7`
* **Descrição**: Servidor de busca semântica de documentação e bibliotecas externas.
* **Ferramentas**: `query-docs`, `resolve-library-id`.
* **Quando Usar**:
  - Pesquisar APIs externas de redes sociais (Pinterest V5) ou bibliotecas estatísticas (SciPy).
  - Obter trechos de documentação atualizados de bibliotecas de terceiros.

### 4. `memory`
* **Descrição**: Gerenciamento de grafo de conhecimento persistente.
* **Ferramentas**: `create_entities`, `create_relations`, `add_observations`, `read_graph`.
* **Quando Usar**:
  - Persistir e mapear correlações e descobertas estruturadas sobre o comportamento do sistema ao longo de diferentes execuções.
  - Construir relacionamentos lógicos entre genomas de sucesso e nichos.

### 5. `sequential-thinking`
* **Descrição**: Engine de raciocínio lógico estruturado por etapas.
* **Ferramentas**: `sequentialthinking`.
* **Quando Usar**:
  - Resolver problemas de debugging altamente complexos, quebrando-os em pensamentos sequenciais interativos.
  - Avaliar trade-offs e comparar abordagens de desenvolvimento passo a passo.

---

## Diretrizes de Prioridade de Ferramentas

1. **Leitura/Diagnóstico**: Priorizar sempre `sqlite` (para estado interno) e `context7` (para documentação externa).
2. **Execução**: Priorizar atuadores determinísticos locais Python. Chame ferramentas do `playwright` MCP apenas para depuração ou validação headful controlada.
3. **Persistência**: Registre descobertas estruturadas no `memory` Graph MCP para acumular inteligência de longo prazo.
