# PADRÕES DE CÓDIGO E PROCESSOS

Todo desenvolvimento no AI Revenue OS deve seguir rigorosamente as regras e o fluxo de engenharia detalhados neste documento.

---

## Processo de Trabalho Obrigatório
Antes de fazer qualquer alteração ou escrever código:

1. **Compreender o problema por completo**: Entender o contexto do bug ou funcionalidade.
2. **Analisar a arquitetura existente**: Identificar o fluxo de dados global afetado.
3. **Localizar os módulos afetados**: Mapear as classes e funções exatas.
4. **Mapear dependências**: Compreender o que depende do módulo modificado.
5. **Identificar possíveis impactos**: Avaliar o risco de quebra colateral.
6. **Consultar documentação oficial**: Consultar guias ou SDKs correspondentes.
7. **Pesquisar soluções modernas**: Buscar melhores práticas de design de software.
8. **Comparar alternativas**: Listar prós e contras de diferentes abordagens.
9. **Justificar a escolha**: Explicar a escolha arquitetural.
10. **Implementar**: Escrever código limpo seguindo os padrões.

---

## Regras Invioláveis de Desenvolvimento

1. **Determinismo sobre Cognição**:
   - **NUNCA** utilize agentes cognitivos ou LLMs para fluxos estruturados e repetitivos (ex: logins, cliques determinísticos em botões, crawling de dados, upload de arquivos). O uso de IA deve ser reservado estritamente para fallbacks cognitivos sob falhas e tratamento de layout.

2. **Cálculos Estatísticos e Financeiros Protegidos**:
   - **NUNCA** altere a matemática e as equações contidas em `src/revenue_os/analytics/` sem executar toda a suite de testes unitários antes e depois da modificação. Qualquer alteração deve manter a consistência matemática causal de cauda única/dupla.

3. **Isolamento de Redes Sociais**:
   - Toda lógica de automação de navegadores, seletores CSS, URLs e cookies de redes sociais deve residir estritamente em `src/reality/` ou `src/execution/`. Nenhuma regra externa de rede social deve vazar para a camada central do `analytics/`.

4. **Preservação de Dados de Produção**:
   - O arquivo `prod_db.sqlite3` é o banco de dados real em Shadow Mode. **NUNCA** apague, limpe ou execute operações destrutivas (`DROP TABLE`, `DELETE` sem WHERE) contra este banco.
   - Testes unitários devem sempre utilizar bancos em memória (`:memory:`) e dados mockados, nunca interagindo com o banco real de produção.

5. **Integridade do Decision Ledger**:
   - O log de decisões `decisions.jsonl` é um livro-caixa *append-only*. Nunca altere registros históricos, limpe linhas antigas ou mude seu formato estruturado.

---

## Estilo e Convenções de Código

* **Tipagem Estrita**: Todos os schemas, contratos de transferência de dados e APIs de entrada/saída devem usar **Pydantic v2** para validação em tempo de execução.
* **Formatação**: O código deve aderir estritamente às convenções do **Ruff** e **Black**.
* **Conventional Commits**: Siga rigorosamente o padrão de commits semânticos:
  - `feat:` (nova funcionalidade)
  - `fix:` (correção de bug)
  - `docs:` (documentação)
  - `test:` (criação/ajuste de testes)
  - `refactor:` (refatoração de código sem alterar comportamento externo)

---

## Testes Unitários e Integração
Sempre valide suas implementações rodando a suite de testes locais:
```powershell
.\venv\Scripts\python -m pytest tests/unit -v
```
Qualquer alteração em classes centrais sem a criação de um teste unitário correspondente em `tests/unit/` será considerada incompleta.
