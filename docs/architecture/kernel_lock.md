# AI Revenue OS — Política de Kernel Lock v1.0

> **Estado da Plataforma**: *Kernel Lock v1.0 Ativo.*  
> O Kernel proprietário do **AI Revenue OS** encontra-se oficial e irrevogavelmente congelado. A construção de novas abstrações de infraestrutura ou classes de framework está encerrada.

---

## 🔒 Módulos sob Kernel Lock v1.0

Os seguintes pacotes e módulos centrais estão sob **Kernel Lock**:

1. `src/revenue_os/analytics/economic_brain.py` (`EconomicBrain`)
2. `src/revenue_os/planning/planning_engine.py` (`PlanningEngine`)
3. `src/revenue_os/events/event_backbone.py` (`EventBackbone`)
4. `src/revenue_os/plugins/plugin_runtime.py` (`PluginRuntime`)
5. `src/revenue_os/connectors/capability_registry.py` (`CapabilityRegistry`)
6. `src/revenue_os/observability/experiment_ledger.py` (`ExperimentLedger`)
7. `src/revenue_os/domain/business_asset.py` (`BusinessAsset`)
8. `src/revenue_os/analytics/genome_library.py` (`GenomeLibrary`)
9. `src/revenue_os/analytics/knowledge_flywheel.py` (`KnowledgeFlywheel`)

---

## 🛡️ Critérios Exclusivos para Alterações no Kernel

Qualquer modificação nos módulos acima exige uma justificativa documental aprovada com base estrita em:

1. **Bug Crítico de Produção**: Falha que impeça a execução do ciclo de receita.
2. **Vulnerabilidade de Segurança**: Correção de vazamento de segredos ou injeção de código.
3. **Problema Comprovado de Produção**: Incompatibilidade identificada durante os Production Milestones.
4. **Melhoria Mensurável de Performance**: Redução comprovada de custos de API ou tempo de execução (>20%).
