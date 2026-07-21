# AI Revenue OS — Matriz de Capacidades Open Source (OSS Capability Matrix v4.0)

> **Diretriz de Orquestração**: *Open Source First. Build Only the Differentiator.*  
> Nenhuma ferramenta de infraestrutura madura será construída internamente. O AI Revenue OS consome exclusivamente capacidades da comunidade Open Source através de adaptadores e plugins desacoplados.

---

## 📊 Matriz de Homologação de Capacidades

| Capacidade | Provedor Primário | Provedor Secundário (Fallback) | Status no AI Revenue OS |
| --- | --- | --- | --- |
| **Landing Pages** | **Astro (SSG / MDX)** | Next.js / Hugo | ✅ Homologado |
| **Workflow Automation** | **n8n** | Activepieces / Windmill | ✅ Homologado |
| **Browser Automation** | **Playwright** | Browser Use / Selenium | ✅ Homologado |
| **Vector Database** | **Qdrant** | Chroma / Milvus | ✅ Homologado |
| **Analytics & Funnels** | **PostHog / GA4** | Umami / Plausible | ✅ Homologado |
| **Headless CMS** | **Directus** | Strapi | ⏳ Planejado |
| **Identity & Auth** | **Authentik** | Keycloak | ⏳ Planejado |
| **Object Storage** | **MinIO (S3 Compatible)** | SeaweedFS / LocalStack | ✅ Homologado |
| **Search Engine** | **Meilisearch** | Typesense | ⏳ Planejado |
| **Message Queue** | **Redis Streams** | NATS / RabbitMQ | ✅ Homologado |
| **Video Generation** | **MoneyPrinterTurbo (MPT)** | MoviePy / FFmpeg | ✅ Homologado |
| **Image Generation** | **NVIDIA FLUX** | ComfyUI / SDXL | ✅ Homologado |
| **Marketplace Connectors** | **Hotmart / ClickBank** | Amazon / Digistore24 / Gumroad | ✅ Homologado |

---

## 🏗️ Estrutura de Plugins Drop-in (`src/revenue_os/plugins/`)

```text
src/revenue_os/plugins/
├── landing/
│   ├── astro/
│   └── nextjs/
├── marketplaces/
│   ├── hotmart/
│   ├── clickbank/
│   └── amazon/
├── video/
│   └── moneyprinter/
├── image/
│   └── flux/
├── analytics/
│   ├── posthog/
│   └── ga4/
└── social/
    └── playwright/
```
