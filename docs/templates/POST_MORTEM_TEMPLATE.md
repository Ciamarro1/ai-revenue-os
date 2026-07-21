# Run Post-Mortem 

**Regra de Ouro**: *Toda nova funcionalidade proposta neste documento deve responder: Qual evidência operacional mostrou que esta mudança é necessária?*

## 1. Contexto da Execução
| Campo | Detalhe |
| :--- | :--- |
| **Run ID** | `RUN_2026_...` |
| **Release Channel** | `[ ] LAB  [ ] SHADOW  [ ] CANARY  [ ] LIMITED  [ ] PRODUCTION` |
| **Data do Run** | `YYYY-MM-DD` |
| **Objetivo** | *[Hipótese econômica ou técnica que estava sendo testada (ex: Validar CTR de vídeos curtos sobre estoicismo)]* |

## 2. Evidências Coletadas (Métricas Reais)
*Resumo quantitativo extraído do Dashboard e APIs parceiras (ex: Pinterest Analytics).*
* **Impressões Totais**: 
* **CTR Médio**: 
* **Engajamento (Salvamentos/Cliques)**: 
* **Custos Operacionais (LLMs/MPT)**: 
* **Taxa de Falha / DLQ**: 
* **Tempos de Renderização (P95)**: 

## 3. Avaliação de Hipóteses
| Status | Hipótese | Observação |
| :---: | :--- | :--- |
| ✅ | **Confirmada**: *[Ex: O formato 9:16 engajou 2x mais]* | *[Dados do mundo real]* |
| ❌ | **Refutada**: *[Ex: Vídeos de 30s custaram mais do que retornaram]* | *[Dados do mundo real]* |

## 4. Incidentes e Resiliência
*Eventos capturados pelo Health Score, OQ e Logs.*
* **Kill Switch / Autopause Acionado?** `[Sim/Não]` *(Motivo)*
* **DLQ (Dead Letters)**: *Quantos experimentos foram abortados em FAILED_PERMANENT?*
* **Retries / Circuit Breakers**: *A API do gerador caiu em algum momento?*

## 5. Decisões para a Próxima Versão (V1.X)
*Lista de ações propostas. Toda ação **DEVE** estar ancorada em uma evidência da seção 2 ou 4.*

| Ação Proposta (Engineering/Economy) | Evidência que Justifica |
| :--- | :--- |
| *[Ex: Trocar provider de voz para X]* | *[Ex: Run Report 124 indicou 30% de falha no provider atual]* |
| *[Ex: Parar de focar em "Quotes"]* | *[Ex: CTR de 0.01% após 72h em Canary, ROI negativo]* |

---
**Assinaturas de Aprovação para V1.X**: ______________
