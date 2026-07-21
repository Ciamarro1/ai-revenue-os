# AI Revenue OS: Dossiê de Investigação e Guia de Contexto (Production Readiness Framework v1.0)

Este documento serve como um **Guia de Contexto Exaustivo** para agentes de Inteligência Artificial e engenheiros. Ele detalha a filosofia, a arquitetura de software, o inventário de arquivos, o esquema de banco de dados e a conclusão oficial das **Sprints de Produção O1 a O8** do **AI Revenue OS**.

---

## 🎯 1. Filosofia Operacional e Propósito do Sistema

O **AI Revenue OS** é uma **Plataforma Operacional de Orquestração Cognitiva e Motor de Alocação Autônoma de Capital** (*Lean Quant Fund*). 

O propósito central do sistema é aplicar as diretrizes **Open Source First. Build Only the Differentiator** e **Zero-Kernel Modification Policy**: orquestrar ferramentas Open Source maduras para infraestrutura enquanto estende suas capacidades exclusivamente através do **AI Revenue OS Plugin SDK (`src/revenue_os/plugins/`)**.

### Diretrizes de Governança & Produção Real:
1. **Kernel Lock v1.0 (Congelamento Definitivo) 🔒**: O Kernel proprietário de decisão (*Economic Brain, Planning Engine, Event Backbone, Capability Registry, Experiment Ledger, Knowledge Flywheel*) encontra-se 100% imutável. Zero modificações no Kernel foram realizadas durante a implementação de todas as Sprints de produção.
2. **Production Readiness Framework (Sprints O1 a O8) 💰**: Todas as 8 Sprints de produção foram implementadas, testadas (81/81 testes no Plugin SDK aprovados) e certificadas como `PRODUCTION` pelo `PluginCertificationEngine`.
3. **Evidence Driven Development (EDD) 📊**: Garantia de que somente dados de proveniência `REAL_PRODUCTION` alteram os pesos do `EconomicBrain`. Benchmarks e testes locais jamais alteram o aprendizado.

---

## 🔄 2. A Máquina de Estados e Pipeline de Produção

O ciclo de vida dos experimentos é orquestrado assincronamente pelo `ExperimentRunner` e estendido via plugins:

```text
 [CREATED] ➔ [RESEARCHED] ➔ [HYPOTHESIS_FORMED] ➔ [ASSET_GENERATED] ➔ [QUALITY_CHECKED]
                                                                     │
 [CALIBRATED] ⮘ [OBSERVED] ⮘ [PUBLISHED] ⮘ [HUMAN_APPROVED] ⮘────────┘
```

---

## 🚀 3. Resumo das Sprints de Produção Concluídas (O1 a O8)

| Sprint | Domínio | Componentes Entregues | Certificação SDK | Status EDD |
|---|---|---|---|---|
| **O1** | Research & Discovery | `ResearchPlugin` (7 provedores: Google Trends, Reddit, HackerNews, RSS, Hotmart, Amazon, Pinterest Trends) | `PRODUCTION` 🏅 | `REAL_PRODUCTION` |
| **O2** | Affiliate Integration | Adaptadores Hotmart, Kiwify, Eduzz e Amazon Associates com resiliência (`RateLimiter`, `CircuitBreaker`) | `PRODUCTION` 🏅 | `REAL_PRODUCTION` / `WAITING_DEP` |
| **O3** | Offer Factory | `ProductionOfferFactory` com 11 geradores determinísticos e selagem SHA-256 | `PRODUCTION` 🏅 | `REAL_PRODUCTION` |
| **O4** | Landing Deployment | `AstroLandingPlugin`, `NextjsLandingPlugin` e `LandingDeploymentEngine` (Cloudflare, Vercel, Netlify) | `PRODUCTION` 🏅 | `REAL_PRODUCTION` |
| **O5** | Creative Generation | `ImageGenerationPlugin` (FLUX/ComfyUI) e `VideoGenerationPlugin` (MPT 9:16/Remotion) com Fila e Fallback | `PRODUCTION` 🏅 | `REAL_PRODUCTION` / `WAITING_DEP` |
| **O6** | Pinterest Automation | `PinterestPlugin` (Playwright Determinístico + Vision Fallback Gemini 2.5 Flash) | `PRODUCTION` 🏅 | `REAL_PRODUCTION` / `WAITING_DEP` |
| **O7** | Production Analytics | `AnalyticsProductionPlugin` (GA4, PostHog, Resend, Webhooks HMAC-SHA256, Callbacks Afiliados) | `PRODUCTION` 🏅 | `REAL_PRODUCTION` / `WAITING_DEP` |
| **O8** | Production Learning | `ProductionLearningPlugin` (Filtro EDD `REAL_PRODUCTION`, Recalibração Bayesiana e Dataset Manager) | `PRODUCTION` 🏅 | `REAL_PRODUCTION` |

---

## 🛡️ 4. Inventário e Arquitetura do Plugin SDK (`src/revenue_os/plugins/`)

- **`src/revenue_os/plugins/research/`**: Plugins de pesquisa de mercado e scoring de oportunidades.
- **`src/revenue_os/plugins/affiliates/`**: Plugins de marketplace de afiliados (Hotmart, Kiwify, Eduzz, Amazon).
- **`src/factory/production/`**: Fábrica determinística de ofertas.
- **`src/revenue_os/plugins/landing/`**: Engine de compilação, deploy e rollback de landing pages.
- **`src/revenue_os/plugins/creatives/`**: Engine de geração de mídias, fila assíncrona, workers e storage manager.
- **`src/revenue_os/plugins/social/`**: Plugin oficial de automação no Pinterest com Playwright e Vision Fallback.
- **`src/revenue_os/plugins/analytics/`**: Plugin de telemetria multicanal, receptores de webhooks e proveniência.
- **`src/revenue_os/plugins/learning/`**: Plugin de aprendizado contínuo e calibração de pesos econômicos.

---

## 💡 5. Diretrizes Para Engenheiros e Agentes de IA

* **Kernel Lock v1.0**: Mantenha o Kernel proprietário 100% intacto. Qualquer novo recurso deve obrigatoriamente estender `BasePlugin` (`src/revenue_os/plugins/base_plugin.py`).
* **Respeite o Protocolo EDD**: Mantenha a distinção entre `REAL_PRODUCTION`, `SIMULATED_BENCHMARK`, `LOCAL_TEST` e `WAITING_EXTERNAL_DEPENDENCY`.
* **Verificação da Suíte**: Execute a suíte de testes antes de qualquer commit:
  ```powershell
  .venv\Scripts\pytest.exe tests/plugins/ -v
  ```
