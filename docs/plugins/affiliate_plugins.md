# Affiliate Provider Plugins Documentation — AI Revenue OS (Sprint O2)

> **Plugins**: `hotmart_affiliate_plugin`, `kiwify_affiliate_plugin`, `eduzz_affiliate_plugin`, `amazon_affiliate_plugin`  
> **Category**: `marketplaces`  
> **SDK Status**: Estendem `BasePlugin` (`src/revenue_os/plugins/base_plugin.py`)  
> **Certification Status**: `PRODUCTION` / `STABLE` 🏅  

---

## 🏛️ Arquitetura de Afiliados

A **Sprint O2 — Affiliate Provider Plugins** implementa adaptadores de marketplace isolados e resilientes sob o Plugin SDK.

```text
                               ┌────────────────────────┐
                               │     PluginRuntime      │
                               └───────────┬────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│  HotmartPlugin   │             │   KiwifyPlugin   │             │   EduzzPlugin    │ ... (Amazon)
└────────┬─────────┘             └────────┬─────────┘             └────────┬─────────┘
         │                                │                                │
         └────────────────────────────────┼────────────────────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
      ┌──────────────────────┐                        ┌──────────────────────┐
      │  Resilience Engine   │                        │   CapabilityReg &    │
      │ (RateLimit/Retry/CB) │                        │    Feature Flags     │
      └──────────────────────┘                        └──────────────────────┘
```

---

## 🛠️ Capacidades por Plugin

Todos os 4 plugins disponibilizam uma interface unificada via `execute(payload)`:

| Ação (`action`) | Função | Payload | Retorno |
|---|---|---|---|
| `discover_products` | Descoberta de produtos por nicho | `{"niche": "tech", "limit": 5}` | Lista de `AffiliateProduct` |
| `get_offer_details` | Detalhes e termos de venda | `{"product_id": "HOT-101"}` | Objeto `OfferDetails` |
| `get_commission_rules` | Regras de repasse e atribuição | `{"product_id": "HOT-101"}` | Objeto `CommissionRule` |
| `generate_deep_link` | Links de afiliado rastreados | `{"product_id": "HOT-101", "sub_id": "c1"}` | Objeto `DeepLinkResponse` |

---

## 🛡️ Motor de Resiliência Integardo (`resilience.py`)

1. **TokenBucketRateLimiter**: Limitação de vazão (padrão 60 req/min) evitando bloqueios por estouro de quota.
2. **ExponentialBackoffRetry**: Repetição automática com tempo de espera exponencial e Jitter aleatório.
3. **CircuitBreaker**: Proteção contra falhas catastróficas em lote (`CLOSED` ➔ `OPEN` ➔ `HALF_OPEN`).

---

## 🚀 Como Utilizar via Runtime

```python
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.affiliates import AffiliatePluginFactory

runtime = PluginRuntime()
hotmart_plugin = AffiliatePluginFactory.create_hotmart_plugin()
runtime.register_plugin(hotmart_plugin)

# Descoberta de Ofertas
result = hotmart_plugin.execute({
    "action": "discover_products",
    "niche": "finance",
    "limit": 3
})
print("Produtos encontrados:", len(result["products"]))

# Geração de Deep Link Rastreável
link_res = hotmart_plugin.execute({
    "action": "generate_deep_link",
    "product_id": result["products"][0]["id"],
    "sub_id": "campaign_pinterest_01"
})
print("Link rastreado:", link_res["deep_link"]["tracking_url"])
```
