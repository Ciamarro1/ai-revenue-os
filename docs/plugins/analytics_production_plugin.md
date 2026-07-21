# Analytics Production Plugin Documentation — AI Revenue OS (Sprint O7)

> **Plugin**: `analytics_production_plugin`  
> **Category**: `analytics`  
> **SDK Status**: Estende `BasePlugin` (`src/revenue_os/plugins/base_plugin.py`)  
> **Certification Status**: `PRODUCTION` / `STABLE` 🏅  

---

## 🏛️ Arquitetura do Analytics Production Plugin

A **Sprint O7 — Analytics Production Plugin** fornece a infraestrutura unificada de telemetria, rastreamento de eventos, ingestão de callbacks de afiliados e auditoria de proveniência (`MetricProvenance`) no Plugin SDK:

```text
               [ Offer Manifest / Landing Page Event ]
                                 │
                                 ▼
                     [ AnalyticsProductionPlugin ] ── BasePlugin (SDK)
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
   [Telemetry Router]    [Affiliate Callback]     [Provenance Tracer]
   (GA4, PostHog, Resend)  (Hotmart, Kiwify, etc)   (SHA-256 HMAC Sign)
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    [ MetricProvenance Envelope ]
                                 │
                                 ▼
                       [ ExperimentLedger ]
```

---

## 🛠️ Ações Disponíveis via Runtime (`execute`)

| Ação (`action`) | Função | Payload de Entrada | Retorno |
|---|---|---|---|
| `track_event` | Roteia evento de telemetria para GA4, PostHog e Resend | `{"event_name": "lead_capture", "properties": {...}}` | Status de cada provedor + Envelope `MetricProvenance` |
| `process_callback` | Processa e normaliza webhooks postback de afiliados | `{"platform": "kiwify", "raw_payload": {...}}` | Objeto `AffiliateCallbackPayload` |
| `sign_webhook` | Gera assinatura HMAC-SHA256 para webhooks de saída | `{"body": {...}}` | Assinatura HMAC hex em `signature` |
| `verify_webhook` | Valida integridade HMAC-SHA256 de webhooks de entrada | `{"body": {...}, "signature": "..."}` | `INVALID_SIGNATURE` ou `SUCCESS` com `MetricProvenance` |

---

## 🔐 Provenance Tracking (`MetricProvenance`)

Cada evento ou callback processado possui um selo imutável de proveniência:
1. **`REAL_PRODUCTION`**: Telemetria remota disparada com sucesso ou webhook de afiliado com assinatura HMAC-SHA256 confirmada.
2. **`SIMULATED_BENCHMARK`**: Telemetria gerada durante testes de carga ou simulações financeiras de portfólio.
3. **`LOCAL_TEST`**: Execução de suíte de testes unitários ou mocks locais.
4. **`WAITING_EXTERNAL_DEPENDENCY`**: Evento registrado quando credenciais/tokens (`GA4_MEASUREMENT_ID`, `POSTHOG_API_KEY`, `RESEND_API_KEY`) estão ausentes no `.env`.

---

## 🚀 Exemplo de Uso via Runtime

```python
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.analytics import AnalyticsPluginFactory

runtime = PluginRuntime()
analytics_plugin = AnalyticsPluginFactory.create_analytics_plugin()
runtime.register_plugin(analytics_plugin)

# Disparo de Telemetria Multicanal
track_res = analytics_plugin.execute({
    "action": "track_event",
    "event_name": "offer_purchased",
    "properties": {
        "offer_id": "OFFER-100",
        "value": 197.00,
        "currency": "BRL"
    }
})
print("Provenance Type:", track_res["provenance"]["provenance_type"])
print("GA4 Response:", track_res["provider_responses"]["ga4"]["status"])

# Processamento de Webhook de Venda Kiwify
cb_res = analytics_plugin.execute({
    "action": "process_callback",
    "platform": "kiwify",
    "raw_payload": {
        "order_id": "KW-PROD-9988",
        "order_ref_amount": 19700,
        "commissions": {"my_commission": 11820}
    },
    "signature": "hmac_verified_signature"
})
print("Comissão Calculada:", cb_res["callback"]["commission"])
```
