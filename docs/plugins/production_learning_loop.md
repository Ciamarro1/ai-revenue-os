# Production Learning Loop Documentation — AI Revenue OS (Sprint O8)

> **Plugin**: `production_learning_plugin`  
> **Category**: `learning`  
> **SDK Status**: Estende `BasePlugin` (`src/revenue_os/plugins/base_plugin.py`)  
> **Certification Status**: `PRODUCTION` / `STABLE` 🏅  

---

## 🏛️ Arquitetura do Production Learning Loop

A **Sprint O8 — Production Learning Loop** conecta todo o histórico de execuções do `ExperimentLedger` aos modelos de decisão e hipóteses do sistema sob a regra absoluta de Evidence Driven Development (EDD):

```text
               [ ExperimentLedger (Evidências de Produção) ]
                                 │
                                 ▼
                     [ ProductionLearningLoop ] ── BasePlugin (SDK)
                                 │
                   (Filtro EDD: REAL_PRODUCTION apenas)
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
 [LearningScheduler]    [ConfidenceUpdate]     [KnowledgeFlywheel]
 (Agendador de Loop)    (Atualização Bayesiana) (Promoção/Rejeição)
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
        [EconomicBrain Weights]         [DatasetVersionManager]
        (Priors Recalibrados)           (Snapshots & Auditabilidade)
```

---

## 🛡️ Regra Inviolável EDD de Aprendizado

> ⚠️ **REGRA ABSOLUTA**:  
> **SOMENTE dados com proveniência classificada estritamente como `REAL_PRODUCTION` alteram os pesos do `EconomicBrain` e o grau de confiança das hipóteses.**  
> Evidências provenientes de `SIMULATED_BENCHMARK` ou `LOCAL_TEST` são gravadas exclusivamente para auditoria e monitoramento, mas **JAMAIS** influenciam o aprendizado ou alteram os pesos econômicos.

---

## 🛠️ Ações Disponíveis via Runtime (`execute`)

| Ação (`action`) | Função | Payload de Entrada | Retorno |
|---|---|---|---|
| `run_cycle` / `recalibrate` | Executa um ciclo completo de aprendizado sob filtragem estrita EDD | `{"entries": [...]}` (opcional) | Objeto `LearningCycleResult` |
| `get_hypotheses` | Consulta o estado atual de todas as hipóteses | `{}` | Lista de `HypothesisState` |
| `get_weights` | Consulta os pesos recalibrados do `EconomicBrain` | `{}` | Lista de `EconomicBrainWeight` |

---

## ⚙️ Dinâmica de Atualização de Hipóteses

1. **Atualização Bayesiana de Confiança (`ConfidenceUpdate`)**:
   - Ajuste proporcional ao número de evidências reais confirmadas.
2. **Promoção de Conhecimento (`KnowledgePromotion`)**:
   - Hipóteses com confiança $\ge 0.85$ são promovidas a **Leis/Princípios Validados** (`PROMOTED_LAW`).
3. **Rejeição de Conhecimento (`KnowledgeRejection`)**:
   - Hipóteses com confiança $\le 0.15$ são desqualificadas e marcadas como **Rejeitadas** (`REJECTED`).
4. **Versionamento do Dataset**:
   - Cada ciclo concluído gera uma tag imutável de versão (`DS-V-YYYYMMDD-HHMM`).

---

## 🚀 Exemplo de Uso via Runtime

```python
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.learning import LearningPluginFactory

runtime = PluginRuntime()
learning_plugin = LearningPluginFactory.create_learning_plugin()
runtime.register_plugin(learning_plugin)

# Execução manual do ciclo de aprendizado
result = learning_plugin.execute({"action": "run_cycle"})
cycle = result["cycle_result"]

print("Cycle ID:", cycle["cycle_id"])
print("Entradas de Produção Real Processadas:", cycle["real_production_entries"])
print("Entradas de Benchmark Ignoradas:", cycle["ignored_benchmark_entries"])
print("Versão do Dataset:", cycle["dataset_version"])

# Consulta dos pesos do EconomicBrain
weights_res = learning_plugin.execute({"action": "get_weights"})
print("Pesos Atuais do EconomicBrain:", weights_res["weights"])
```
