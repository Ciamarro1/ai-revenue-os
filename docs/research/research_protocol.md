# PROTOCOLO DE PESQUISA (RESEARCH PROTOCOL)

Antes de alterar qualquer código ou introduzir novas bibliotecas, o Chief Cognitive Engineer deve realizar uma fase rigorosa de pesquisa estruturada para garantir a robustez da solução.

---

## 1. Fontes Oficiais e Ferramentas de Pesquisa

Toda pesquisa técnica deve priorizar as seguintes fontes de dados e ferramentas:
* **Documentação Oficial dos Provedores**: Consultar sempre as APIs de terceiros (ex: Pinterest Developer Docs para endpoints V5) antes de assumir comportamentos de rede.
* **Context7 (MCP Server)**: Executar buscas semânticas para localizar trechos de documentação atualizados e exemplos reais de uso de classes e SDKs.
* **DeepWiki & GitHub**: Buscar discussões de issues, RFCs, e changelogs oficiais dos pacotes (como Playwright Python ou Pydantic) para mapear bugs conhecidos ou mudanças de APIs obsoletas.
* **Scratch Scripts**: Escrever pequenos trechos experimentais isolados na pasta `<conversation-id>/scratch/` para verificar retornos e comportamentos de bibliotecas de forma empírica.

---

## 2. Processo de Investigação em 3 Etapas

### Etapa A: Mapeamento de Dependências
* Identifique quais módulos da Clean Architecture importam ou são importados pelo arquivo a ser modificado.
* Verifique se a mudança afeta os modelos de dados Pydantic (`schemas.py`) ou o banco de dados relacional.

### Etapa B: Análise Comparativa de Alternativas
Sob problemas de design complexos, avalie pelo menos duas soluções possíveis, documentando:
1. **Trade-offs técnicos**: Facilidade de implementação vs. desempenho computacional.
2. **Impacto na observabilidade**: Como rastrear erros e registrar tempos com `TimingContext`.
3. **Riscos de infraestrutura**: Consumo de memória RAM, CPU e limites de chamadas de API (Rate Limits).

### Etapa C: Justificativa Técnica
* Apresente a decisão em formato estruturado ao operador humano ou ao log de decisões (ADR), explicando por que a abordagem escolhida é superior no longo prazo.
* **Nunca** selecione um caminho baseado apenas em rapidez de escrita de código (código temporário ou gambiarras).
