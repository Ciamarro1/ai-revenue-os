# AI Revenue OS — Mapa de Capacidades (Capability Map)

> **Diretriz de Orquestração**: *Capability ➔ Open Source Provider ➔ Adapter ➔ Internal Interface ➔ Business Module*  
> O **AI Revenue OS** consome interfaces abstratas desacopladas de qualquer software proprietário específico. A troca de uma ferramenta Open Source por outra ocorre sem alterar a lógica de decisão ou o código de negócios.

---

## 🗺️ Mapeamento de Capacidades do Ecossistema

| Capacidade | Provedor Open Source | Adaptador Interno | Interface Python | Módulo de Negócios |
| --- | --- | --- | --- | --- |
| **Landing Generation** | Astro / Next.js | `AstroLandingAdapter` | `ILandingProvider` | `OfferFactory` |
| **Video Generation** | MoneyPrinterTurbo / MoviePy | `MoneyPrinterVideoAdapter` | `IVideoGenerator` | `ContentFactory` |
| **Browser Automation** | Playwright / Chromium | `PlaywrightSocialAdapter` | `ISocialPublisher` | `DistributionEngine` |
| **Vector Database** | Qdrant / Chroma | `QdrantVectorAdapter` | `IVectorStore` | `KnowledgeFlywheel` |
| **Relational Database** | PostgreSQL / SQLite | `SQLiteDatabaseAdapter` | `IDatabaseBackend` | `CognitiveRepository` |
| **Analytics Dashboards** | Grafana / Metabase | `GrafanaTelemetryAdapter` | `IMetricsExporter` | `ObservabilityEngine` |
| **Workflow Automation** | n8n / Windmill | `N8nWorkflowAdapter` | `IWorkflowEngine` | `TaskOrchestrator` |
| **Object Storage** | MinIO / S3 | `MinIOStorageAdapter` | `IObjectStorage` | `AssetManager` |
| **Search Engine** | Meilisearch / Typesense | `MeilisearchAdapter` | `ISearchEngine` | `OpportunityEngine` |
| **Message Queue** | Redis Streams / NATS | `RedisQueueAdapter` | `IMessageQueue` | `QueueWorker` |

---

## 📐 Exemplo de Fluxo de Desacoplamento

```text
[ Business Module: OfferFactory ]
               │
               ▼
[ Interface: ILandingProvider ]
               │
               ▼
[ Adapter: AstroLandingAdapter ]
               │
               ▼
[ Open Source Engine: Astro (SSG + MDX) ]
```

Se o provedor **Astro** for substituído por **Next.js** ou **Hugo**:
1. O módulo `OfferFactory` permanece 100% intocado.
2. Apenas o adaptador `NextJsLandingAdapter` é registrado no `CapabilityRegistry`.
