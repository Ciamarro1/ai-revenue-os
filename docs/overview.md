# AI Revenue OS: Visão Geral e Fluxo Operacional (v3.0)

O **AI Revenue OS (v3.0)** é uma **Plataforma de Orquestração Cognitiva e Motor de Alocação Autônoma de Capital** (*Lean Quant Fund*).

O objetivo principal do sistema não é simplesmente "criar e postar vídeos", mas **descobrir e validar cientificamente ofertas de receita (`RevenueOpportunity`) e variações de conteúdo (`Genome`) que gerem lucro com maior probabilidade e menor risco**, escalando os vencedores de forma automatizada com a restrição **Open Source First**.

---

## 🎯 1. O Objetivo Principal e Filosofia Open Source First

O sistema resolve a aleatoriedade da viralização e da monetização dividindo sua operação em duas grandes fases estratégicas:

1. **Organic Discovery Mode (Modo de Descoberta Orgânica) 🌱**
   - **Foco:** Encontrar tendências e testar ideias no tráfego orgânico sem gastar capital financeiro (alocando apenas poder computacional/GPU e quotas de postagem).
   - **Recompensa:** Avaliada em taxas de cliques (CTR), salvamentos e receita gerada. O conteúdo vencedor é catalogado na `Genome Library`.
   
2. **Paid Scaling Mode (Modo de Escala Paga) 💰**
   - **Foco:** Injetar dinheiro real (anúncios pagos) apenas nos genomas e ativos de negócios (`BusinessAsset`) que foram provados e validados no tráfego orgânico.
   - **Recompensa:** Avaliada estritamente em retorno financeiro real (ROAS, Margem e LTV), aplicando filtros rígidos de controle de risco (*Stop-Loss*) gerenciados pelo `PortfolioManager`.

---

## 🔄 2. O Fluxo Operacional (A Máquina de Estados)

Toda a orquestração do projeto é executada de forma assíncrona e sequencial em um loop fechado controlado pelo `ExperimentRunner` através de **9 estados principais**:

```text
 [CREATED] ➔ [RESEARCHED] ➔ [HYPOTHESIS_FORMED] ➔ [ASSET_GENERATED] ➔ [QUALITY_CHECKED]
                                                                     │
 [CALIBRATED] ⮘ [OBSERVED] ⮘ [PUBLISHED] ⮘ [HUMAN_APPROVED] ⮘────────┘
```

---

## 🏗️ 3. A Arquitetura de Orquestração em Camadas (v3.0)

```text
                Economic Brain
                       │
               Planning Engine
                       │
              Capability Registry
                       │
               Plugin Runtime
                       │
          ┌────────────┼────────────┐
          │            │            │
      Astro      Playwright    MoneyPrinter
          │            │            │
          └────────────┼────────────┘
                       │
                Event Backbone
                       │
             Knowledge Flywheel
```

- **Economic Brain**: Otimiza a função objetivo $\text{Utility} = \text{Revenue} - \text{InfraCost} - \text{RiskPenalty} + \text{KnowledgeGain} + \text{ReusabilityGain}$.
- **Planning Engine**: Traduz metas de receita em planos de execução DAG sequenciais de 6 etapas.
- **Capability Registry**: Gerencia a associação entre capacidades abstratas e provedores Open Source homologados (Primário + Fallbacks).
- **Plugin Runtime**: Executa plugins via interface imutável `BasePlugin` com failover autônomo.
- **Event Backbone**: Barramento Pub/Sub desacoplado transmitindo eventos de domínio (`research.topic.created`, `opportunity.selected`, `offer.generated`, `landing.published`, `traffic.received`, `conversion.recorded`, `genome.updated`, `knowledge.learned`).
- **Knowledge Flywheel**: Converte medições do mundo real em regras de aprendizado contínuo.

---

## 🛡️ 4. Mecanismos de Segurança e Prontidão de Produção (Sprint P1)

* **Circuit Breaker & Production Readiness**: O `ProductionReadinessEngine` impõe limite de orçamento diário e executa retentativa e recuperação automática pós-crash de experimentos paralisados.
* **Secrets Governance**: O `SecretsManager` mascara chaves sensíveis em logs (`sk-p...8a9f`) e garante o isolamento entre ambientes.
* **Decision DAG & Sealing**: O `ExplainabilityEngine` reconstrói gráficos auditáveis de decisão e lacra os ativos validados.
