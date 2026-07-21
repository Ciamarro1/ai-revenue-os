# AI Revenue OS — Definition of Done (Production v5.5 LTS)

> **Regra de Homologação**: *Nenhum Production Milestone (PM-1 a PM-5) é marcado como Concluído sem cumprir integralmente os 7 critérios do Definition of Done.*

---

## 📋 Os 7 Critérios do Definition of Done (DoD)

1. **Aprovação de Testes (`pytest`)**: 100% dos testes unitários e de integração verdes sem erros.
2. **Certificação de Plugin (`PluginCertificationEngine`)**: Todos os plugins utilizados no ciclo devem possuir status `PRODUCTION` ou `STABLE`.
3. **Registro no Experiment Ledger (`ExperimentLedger`)**: Dados imutáveis gravados com sucesso em `knowledge/experiment_ledger.jsonl`.
4. **Publicação no Event Backbone (`EventBackbone`)**: Eventos de domínio transmitidos e escutados sem perda de mensagens.
5. **Observabilidade e Tracing**: Telemetria, latência e custo registrados e mascarados pelo `SecretsManager`.
6. **Linhagem e Rollback Rastreáveis (`DatasetVersionManager`)**: Versões de Dataset, Conhecimento e Genoma vinculadas.
7. **Execução Real em Produção**: Ciclo validado em ambiente físico (sem mocks) obtendo métricas de produção.
