# Pinterest Automation Plugin Documentation — AI Revenue OS (Sprint O6)

> **Plugin**: `pinterest_plugin`  
> **Category**: `social`  
> **SDK Status**: Estende `BasePlugin` (`src/revenue_os/plugins/base_plugin.py`)  
> **Certification Status**: `PRODUCTION` / `STABLE` 🏅  

---

## 🏛️ Arquitetura do PinterestPlugin

A **Sprint O6 — Pinterest Automation (PinterestPlugin)** encapsula o pipeline híbrido de automação social no Plugin SDK:

```text
               [ OfferManifest / EnrichedOfferManifest ]
                                 │
                                 ▼
                      [ PinterestPlugin ] ── BasePlugin (SDK)
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
[PublicationQueue]       [Session & Cookie]      [Safety & RateLimit]
(Retry + Screenshots)    (config/sessions/)      (Cooldown/Diversity)
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       [Playwright Publisher]        [Vision/Cognitive Fallback]
       (Execution Layer UI)          (Gemini 2.5 Flash / MPT)
                 │                               │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
             [ ExperimentLedger (WAITING_EXTERNAL_DEP) ]
```

---

## 🛠️ Ações Disponíveis via Runtime (`execute`)

| Ação (`action`) | Função | Payload de Entrada | Retorno |
|---|---|---|---|
| `publish` | Executa a publicação do Pin | `{"media_path": "...", "title": "...", "description": "...", "link": "..."}` | Objeto `PinterestPublishResult` |
| `enqueue` | Adiciona um Pin à fila de publicação | `{"media_path": "...", "title": "..."}` | Objeto `PublicationJob` |
| `process_queue` | Consome e processa o próximo job da fila com retries | `{}` | Job atualizado + `PinterestPublishResult` |
| `get_metrics` | Captura métricas (views, clicks, saves) | `{"pin_id": "12345"}` | Métricas canônicas |
| `check_session` | Verifica a validade dos cookies | `{}` | `{"has_session": true/false}` |
| `archive_content` | Deleta/Arquiva um Pin | `{"content_id": "12345"}` | `{"status": "SUCCESS"}` |

---

## 🔐 Gestão de Cookies e Classificação Estrita EDD

1. **Sessão & Cookies**: Localizados em `config/sessions/pinterest.json`. O plugin verifica proativamente a presença e validade dos cookies.
2. **Execução sob EDD**:
   - **Com Sessão / Token Válido**: Publicação real física executada com retorno `REAL_PRODUCTION`.
   - **Sem Sessão / Credenciais Ausentes (e `mode != shadow`)**: Retorno automático com status `WAITING_EXTERNAL_DEPENDENCY`, impedindo falsos positivos de produção.
   - **Modo Shadow (`mode = shadow`)**: Simulação controlada de publicação com retorno `LOCAL_TEST`.

---

## 📸 Screenshots de Diagnóstico & Vision Fallback

1. **Screenshots de Auditoria**: Em caso de anomalia de UI ou falha durante o workflow Playwright, uma captura de tela é gravada em `storage/screenshots/pinterest/error_{timestamp}.png`.
2. **Fallback Cognitivo em 3 Etapas**:
   - **Etapa 1**: Playwright Determinístico via seletores de UI.
   - **Etapa 2**: Vision Fallback usando Gemini 2.5 Flash via OpenRouter.
   - **Etapa 3**: OpenManus CLI como fallback final.

---

## 🚀 Exemplo de Uso via Runtime

```python
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.social import SocialPluginFactory, PinterestConfig

runtime = PluginRuntime()
pinterest_plugin = SocialPluginFactory.create_pinterest_plugin(
    PinterestConfig(mode="shadow", session_file_path="config/sessions/pinterest.json")
)
runtime.register_plugin(pinterest_plugin)

# Publicação de Pin Promocional
result = pinterest_plugin.execute({
    "action": "publish",
    "media_path": "storage/creatives/images/mockup.png",
    "title": "Curso Master AI — Oferta Exclusiva",
    "description": "Aprenda a construir sistemas autônomos de receita com IA.",
    "link": "https://pages.airevenueos.com/curso-master-ai"
})

print("Pin ID:", result["result"]["pin_id"])
print("Status:", result["result"]["status"])
print("Classificação EDD:", result["result"]["classification_status"])
```
