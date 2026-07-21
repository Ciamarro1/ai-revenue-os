# AI Revenue OS — Diretriz: Evidence Driven Development (EDD v4.5)

> **Princípio Fundamental**: *Nenhum código de Kernel sem Evidência de Produção.*  
> O desenvolvimento e a evolução do **AI Revenue OS** são estritamente guiados por dados de produção, testes empíricos e evidências científicas. Intuições arquiteturais sem validação por métricas reais são proibidas.

---

## 📜 As 5 Regras Invioláveis do EDD

### Regra #1 — Trava do Kernel por Evidência Operacional
Nenhum novo módulo, classe ou abstração pode ser adicionado ao Kernel proprietário sem a apresentação prévia de evidências operacionais de produção demonstrando que as abstrações existentes são insuficientes.

### Regra #2 — Cobertura de Bugs por Testes Antecipados
Todo bug ou regressão identificado em produção deve obrigatoriamente gerar um teste automatizado (`pytest`) que reproduza a falha **antes** de qualquer alteração de código. O código só é promovido quando o novo teste passar de VERMELHO para VERDE.

### Regra #3 — Isolamento via Plugins e Adaptadores
Toda nova integração com APIs externas, plataformas de distribuição, bancos de dados, geradores de mídias ou marketplaces deve ser implementada exclusivamente como **Plugin Drop-in** ou **Adapter desacoplado** na pasta `src/revenue_os/plugins/` ou `src/revenue_os/connectors/`.

### Regra #4 — Alterações no Economic Brain por Ganhos Estatísticos
Mudanças nas fórmulas de utilidade, pesos de risco ou métricas do `EconomicBrain` só são autorizadas quando o histórico do `ExperimentLedger` comprovar ganho consistente de receita ou redução de custos por experimento.

### Regra #5 — Rastreadilidade Causal Completa
Toda hipótese, decisão financeira ou alteração de portfólio deve ser rastreável até os experimentos e dados que a sustentam através da linhagem:
$$\text{Dataset Version} \rightarrow \text{Knowledge Version} \rightarrow \text{Genome Version} \rightarrow \text{Decision DAG}$$
