# AI Revenue OS - Production v1.0 Protocol

Roteiro disciplinado para a transição do sistema da fase de *Feature Freeze* (desenvolvimento) para o *Production Freeze* (validação real). 

*Regra de Ouro da V1.1 em diante: Toda nova funcionalidade deve responder "Qual evidência operacional mostrou que esta mudança é necessária?" (Run Report, Decisions Ledger, Health Score, OQ ou Canary).*

## Fase 1 — Validar a Infraestrutura
*Foco: Corrigir apenas o necessário para passar nos testes.*
- [x] Aplicar todas as migrations (`001` a `005`).
- [x] Executar OQ-F (Functional).
- [x] Executar OQ-P (Performance).
- [x] Executar Chaos Test.
- [x] Executar Recovery Test.
- [x] Executar Burn-in Test.
- [x] Confirmar Dashboard operante e Health Score saudável.

## Fase 2 — Canary Release
*Foco: Contato inicial controlado com a economia externa.*
- [x] Promover sistema para Release Channel: CANARY.
- [x] Publicar apenas os 3 vídeos previstos no Pinterest.
- [x] Confirmar fluxo completo: Bundle gerado, Manifest selado, Decisions Ledger preenchido, Event Log completo.
- [x] Confirmar Health Score normal.
- [x] Confirmar que nenhum Kill Switch foi acionado.

## Fase 3 — Espera Operacional
*Foco: Nenhuma alteração de código. Apenas observação (24-72h).*
- [ ] Coletar Impressões reais.
- [ ] Coletar CTR.
- [ ] Coletar Salvamentos/Engajamento.
- [ ] Monitorar eventuais erros de publicação atrasados.
- [ ] Apurar Custos da operação (APIs / MPT).
- [ ] Monitorar tempo real de calibração.

## Fase 4 — Pós-Mortem e Decisão
*Foco: Planejamento baseado em evidências empíricas.*
- [ ] Produzir Relatório Único contendo:
  - O que funcionou conforme esperado.
  - O que não funcionou.
  - Quais hipóteses foram confirmadas.
  - Quais hipóteses foram refutadas.
  - Quais mudanças passam a ter prioridade.
- [ ] Declarar **Production Freeze** formal.
- [ ] Iniciar V1.1 com base estrita no Pós-Mortem.
