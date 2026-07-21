# ResearchPlugin Documentation — AI Revenue OS (Sprint O1)

> **Plugin Name**: `research_plugin`  
> **Category**: `research`  
> **SDK Status**: Estende `BasePlugin` (`src/revenue_os/plugins/base_plugin.py`)  
> **Certification Status**: `PRODUCTION` / `STABLE` 🏅  

---

## 🏛️ Arquitetura Geral

O `ResearchPlugin` é a peça central da **Sprint O1 — Research Plugin**, projetado para descobrir oportunidades de mercado em tempo real agregando múltiplos provedores desacoplados sem alterar o Kernel do sistema.

```text
                               ┌────────────────────────┐
                               │     PluginRuntime      │
                               └───────────┬────────────┘
                                           │
                               ┌───────────▼────────────┐
                               │     ResearchPlugin     │
                               └───────────┬────────────┘
                                           │
            ┌──────────────────────────────┼──────────────────────────────┐
            │                              │                              │
┌───────────▼────────────┐    ┌────────────▼───────────┐     ┌────────────▼───────────┐
│    ProviderRegistry    │    ┌     CacheService       │     │  DeduplicationService  │
└───────────┬────────────┘    └────────────────────────┘     └────────────────────────┘
            │
 ┌──────────┼──────────┬──────────┬──────────┬──────────┬──────────┐
 ▼          ▼          ▼          ▼          ▼          ▼          ▼
Google    Reddit     Hacker      RSS      Hotmart    Amazon    Pinterest
Trends     API        News      Feed      Adapter   Adapter     Trends
```

---

## 🔌 Provedores Suportados (7 Adaptadores)

| Provedor | Tipo | Classificação EDD | Origem dos Dados |
|---|---|---|---|
| **GoogleTrendsProvider** | Public RSS | `REAL_PRODUCTION` / `LOCAL_TEST` | Daily Trends RSS (`https://trends.google.com`) |
| **RedditProvider** | Public JSON | `REAL_PRODUCTION` / `LOCAL_TEST` | API Pública JSON (`https://reddit.com/r/{sub}/hot.json`) |
| **HackerNewsProvider** | Firebase REST | `REAL_PRODUCTION` / `LOCAL_TEST` | Official HN Firebase API (`v0/topstories.json`) |
| **RSSProvider** | Generic XML | `REAL_PRODUCTION` / `LOCAL_TEST` | XML/Atom Feeds configuráveis |
| **HotmartProvider** | Marketplace | `LOCAL_TEST` / `WAITING_EXTERNAL_DEPENDENCY` | Vitrine de produtos e comissões |
| **AmazonProvider** | Marketplace | `LOCAL_TEST` / `WAITING_EXTERNAL_DEPENDENCY` | Best Sellers e ofertas em alta |
| **PinterestTrendsProvider** | Social Trends | `LOCAL_TEST` / `WAITING_EXTERNAL_DEPENDENCY` | Pesquisas virais e Pins |

---

## ⚙️ Configuração Pydantic v2

```python
from src.revenue_os.plugins.research import ResearchPluginFactory, ResearchPluginConfig

config = ResearchPluginConfig(
    cache_enabled=True,
    cache_ttl_seconds=3600,
    dedup_enabled=True,
    max_results_per_provider=10,
    min_score_threshold=0.50,
    enable_google_trends=True,
    enable_reddit=True,
    enable_hackernews=True,
    enable_rss=True,
    enable_hotmart=True,
    enable_amazon=True,
    enable_pinterest=True
)

plugin = ResearchPluginFactory.create_plugin(config)
plugin.initialize()
```

---

## 🚀 Como Executar no Runtime

```python
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.research import ResearchPluginFactory

runtime = PluginRuntime()
plugin = ResearchPluginFactory.create_plugin()
runtime.register_plugin(plugin)

result = runtime.execute_capability("research_discovery", {
    "niche": "python",
    "limit": 5,
    "force_refresh": False
})

print("Oportunidades encontradas:", result["returned_count"])
```

---

## ➕ Como Adicionar um Novo Provedor (Open-Closed Principle)

Para adicionar um novo adaptador sem alterar nenhum código existente:

1. Crie a classe estendendo `OpportunityProvider`:

```python
from src.revenue_os.plugins.research.providers import OpportunityProvider
from src.revenue_os.plugins.research.models import ResearchOpportunity

class MyCustomProvider(OpportunityProvider):
    @property
    def provider_name(self) -> str:
        return "my_custom_provider"

    def fetch_opportunities(self, niche: str, limit: int = 10):
        # Implemente a lógica de coleta aqui
        return [...]
```

2. Registre no `ProviderRegistry`:

```python
plugin.registry.register(MyCustomProvider())
```

Pronto! O novo provedor participará automaticamente do ciclo de coleta, deduplicação e pontuação.
