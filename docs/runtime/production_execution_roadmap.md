# Production Execution Roadmap — AI Revenue OS (v1.0 Operations)

> **Diretriz Operacional**: *Sem novas expansões arquiteturais no Kernel (Kernel Lock v1.0). Foco total em execução real, tráfego, publicação e receita.*

---

## 🏃 Sprint O1 — Research Plugin (Oportunidades Reais) [STATUS: ✅ CONCLUÍDO / PRODUCTION CERTIFIED]
- **Objetivo**: Descobrir demandas reprimidas e nichos lucrativos no mundo real conectando APIs de tendência.
- **Implementação**: `ResearchPlugin` via `BasePlugin` (`src/revenue_os/plugins/research/`).
- **Capacidade OSS & Adapters**: Google Trends, Reddit, Hacker News, RSS, Hotmart, Amazon, Pinterest Trends.
- **Saída Canônica**: Objeto `ResearchOpportunity` (compatível com `RevenueOpportunity`).
- **Critério EDD**: `metric_source = REAL_PRODUCTION` registrado no `ExperimentLedger`. Certificado como `PRODUCTION` pelo `PluginCertificationEngine`.

---

## 🏃 Sprint O2 — Affiliate Provider Plugins (Adapters de Marketplace) [STATUS: ✅ CONCLUÍDO / PRODUCTION CERTIFIED]
- **Objetivo**: Integrar os marketplaces de afiliados para busca automatizada de produtos de alta conversão.
- **Implementação**:
  - `HotmartAffiliatePlugin` (`src/revenue_os/plugins/affiliates/hotmart_plugin.py`)
  - `KiwifyAffiliatePlugin` (`src/revenue_os/plugins/affiliates/kiwify_plugin.py`)
  - `EduzzAffiliatePlugin` (`src/revenue_os/plugins/affiliates/eduzz_plugin.py`)
  - `AmazonAffiliatePlugin` (`src/revenue_os/plugins/affiliates/amazon_plugin.py`)
- **Capacidades**: Product Discovery, Offer Details, Commission Rules, Deep Link Generation, Rate Limiter, Retry e Circuit Breaker.
- **Saída Canônica**: Objetos `AffiliateProduct`, `OfferDetails`, `CommissionRule` e `DeepLinkResponse`.
- **Critério EDD**: Certificados como `PRODUCTION` pelo `PluginCertificationEngine` com resiliência testada.

---

## 🏃 Sprint O3 — Offer Factory Production [STATUS: ✅ CONCLUÍDO / PRODUCTION CERTIFIED]
- **Objetivo**: Combinar Oportunidade, Produto de Afiliado e Genoma Criativo em uma Oferta Irresistível.
- **Implementação**: `ProductionOfferFactory` (`src/factory/production/production_offer_factory.py`).
- **Geradores Determinísticos**: Headline, Benefits, Pain Points, CTA, SEO, Keywords, Image Prompts (FLUX), Video Prompts (MPT), Landing (Astro/Next), Pinterest (Playwright) e Analytics (GA4/PostHog).
- **Entrada**: `RevenueOpportunity` + `AffiliateProduct` + `Genome`.
- **Saída Canônica**: Objeto `EnrichedOfferManifest` selado criptograficamente com `inputs_hash` e `signature_hash`.
- **Critério EDD**: Auditado e registrado com sucesso no `ExperimentLedger` (`metric_source = REAL_PRODUCTION`).

---

## 🏃 Sprint O4 — Landing Deployment (Astro & Next.js) [STATUS: ✅ CONCLUÍDO / PRODUCTION CERTIFIED]
- **Objetivo**: Compilar e publicar fisicamente landing pages de alta conversão no ar.
- **Implementação**:
  - `AstroLandingPlugin` (`src/revenue_os/plugins/landing/astro_plugin.py`)
  - `NextjsLandingPlugin` (`src/revenue_os/plugins/landing/nextjs_plugin.py`)
  - `LandingDeploymentEngine` (`src/revenue_os/plugins/landing/deployment_engine.py`)
- **Provedores CDN**: Cloudflare Pages, Vercel e Netlify.
- **Capacidades**: Build Automático, Deploy Automático, Rollback Instantâneo, Versionamento e Fingerprints SHA-256.
- **Saída Canônica**: URL pública ativa (`https://...`), `DeploymentRecord` e `RollbackRecord`.
- **Critério EDD**: Certificados como `PRODUCTION` pelo `PluginCertificationEngine` com auditoria no `ExperimentLedger` (`metric_source = REAL_PRODUCTION`).

---

## 🏃 Sprint O5 — Creative Generation (Automação de Mídia) [STATUS: ✅ CONCLUÍDO / PRODUCTION CERTIFIED]
- **Objetivo**: Gerar ativos visuais e vídeos 9:16 em lote.
- **Implementação**:
  - `ImageGenerationPlugin` (`src/revenue_os/plugins/creatives/image_plugin.py`)
  - `VideoGenerationPlugin` (`src/revenue_os/plugins/creatives/video_plugin.py`)
  - `CreativeBenchmarkEngine` (`src/revenue_os/plugins/creatives/benchmark_engine.py`)
- **Provedores Gerativos**: FLUX.1-schnell, ComfyUI, MoneyPrinterTurbo e Remotion.
- **Mecanismos de Produção**: Fila de Jobs com prioridade (`CreativeJobQueue`), Worker Pool assíncrono, Retry Exponential Backoff, Fallback entre provedores, Hashes SHA-256 e Versionamento (`v1.0.0-img-timestamp`).
- **Saída Canônica**: Mídias físicas mp4/png registradas em `storage/creatives/` com fingerprint SHA-256.
- **Critério EDD**: Certificados como `PRODUCTION` pelo `PluginCertificationEngine` com auditoria no `ExperimentLedger` (`metric_source = REAL_PRODUCTION`).

---

## 🏃 Sprint O6 — Pinterest Automation (PinterestPlugin) [STATUS: ✅ CONCLUÍDO / PRODUCTION CERTIFIED]
- **Objetivo**: Publicar fisicamente Pins com links de afiliado rastreados no Pinterest.
- **Implementação**:
  - `PinterestPlugin` (`src/revenue_os/plugins/social/pinterest_plugin.py`)
- **Capacidades**:
  - Leitura e restauração de cookies em `config/sessions/pinterest.json`.
  - Publicação Híbrida: Rota Playwright Determinística ➔ Vision Fallback (Gemini 2.5 Flash) ➔ OpenManus CLI.
  - Fila de Publicação Assíncrona (`PublicationQueue`), Retries, Captura de Screenshots de Diagnóstico (`storage/screenshots/pinterest/`).
  - Rate Limiter & Safety Coordinator para proteção anti-bloqueio.
  - Extração de Analytics (Impressões, Cliques, Salvamentos).
- **Saída Canônica**: URL pública do Pin publicado (`https://www.pinterest.com/pin/...`).
- **Critério EDD**: Certificado como `PRODUCTION` pelo `PluginCertificationEngine`. Classificado como `WAITING_EXTERNAL_DEPENDENCY` quando não há sessão ou credenciais configuradas.

---

## 🏃 Sprint O7 — Analytics Production [STATUS: ✅ CONCLUÍDO / PRODUCTION CERTIFIED]
- **Objetivo**: Conectar telemetria multicanal, webhooks assinados e pós-venda de afiliados a dashboards e rastreabilidade de proveniência.
- **Implementação**:
  - `AnalyticsProductionPlugin` (`src/revenue_os/plugins/analytics/analytics_plugin.py`)
- **Capacidades**:
  - Roteamento de telemetria server-side para GA4 Measurement Protocol, PostHog e Resend.
  - Processamento de callbacks de afiliados (Hotmart, Kiwify, Eduzz, Amazon).
  - Gestão de Webhooks Assinados via HMAC-SHA256 (`SignedWebhookManager`).
  - Rastreabilidade de Proveniência (`MetricProvenance`: `REAL_PRODUCTION`, `SIMULATED_BENCHMARK`, `LOCAL_TEST`, `WAITING_EXTERNAL_DEPENDENCY`).
- **Saída Canônica**: Registro de telemetria e pós-venda auditado com envelope de proveniência e selagem SHA-256 no `ExperimentLedger`.
- **Critério EDD**: Certificado como `PRODUCTION` pelo `PluginCertificationEngine`.

---

## 🏃 Sprint O8 — Production Learning Loop [STATUS: ✅ CONCLUÍDO / PRODUCTION CERTIFIED]
- **Objetivo**: Fechar o ciclo científico conectando a telemetria ao aprendizado de produção.
- **Implementação**:
  - `ProductionLearningPlugin` (`src/revenue_os/plugins/learning/learning_plugin.py`)
  - `ProductionLearningEngine` (`src/revenue_os/plugins/learning/engine.py`)
  - `LearningScheduler` (`src/revenue_os/plugins/learning/scheduler.py`)
- **Capacidades**:
  - Filtragem Estrita EDD: Apenas evidências `REAL_PRODUCTION` alteram os pesos do `EconomicBrain`.
  - Atualização Bayesiana de Confiança (`ConfidenceUpdate`).
  - Promoção de Hipótese para Lei Validada (`KnowledgePromotion` $> 0.85$).
  - Rejeição e Arquivamento de Hipótese Refutada (`KnowledgeRejection` $< 0.15$).
  - Recalibração de Priors e Versionamento do Dataset (`DatasetVersionManager`).
- **Saída Canônica**: `LearningCycleResult` registrado no `ExperimentLedger`.
- **Critério EDD**: Certificado como `PRODUCTION` pelo `PluginCertificationEngine`.
- **Fluxo**:
  ```text
  ExperimentLedger (REAL_PRODUCTION) ➔ EconomicBrain ➔ GenomeLibrary ➔ CalibrationEngine
  ```
- **Resultado**: Re-alocação automática de verbas para os genomas de maior ROI comprovado no mundo real.

---

## 📋 Checklist Obrigatório de DoD para Cada Plugin

Para que qualquer Plugin seja marcado como `[x] Concluído`, ele deve satisfazer 100% dos critérios:
- [ ] Código implementado estendendo `BasePlugin`
- [ ] Testes unitários e de integração verdes (`pytest`)
- [ ] Certificado via `PluginCertificationEngine`
- [ ] Integração física real executada contra serviço ou sandbox oficial
- [ ] Evento de domínio publicado no `EventBackbone`
- [ ] Métricas gravadas no banco de dados com `metric_source = REAL_PRODUCTION`
- [ ] Telemetria de erro e resiliência testada via `ChaosEngine`
- [ ] Documentação técnica atualizada
- [ ] Evidência persistida no `ExperimentLedger`
