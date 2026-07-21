# Landing Deployment Engine Documentation — AI Revenue OS (Sprint O4)

> **Plugins**: `astro`, `nextjs`  
> **Category**: `landing`  
> **SDK Status**: Estendem `BasePlugin` (`src/revenue_os/plugins/base_plugin.py`)  
> **Certification Status**: `PRODUCTION` / `STABLE` 🏅  

---

## 🏛️ Arquitetura do Landing Deployment Engine

A **Sprint O4 — Landing Deployment Engine** possibilita compilação estática, selagem de fingerprints SHA-256, versionamento, deploys automáticos em CDNs e rollback instantâneo para Landing Pages geradas pelo sistema.

```text
               [ EnrichedOfferManifest (Sprint O3) ]
                                 │
                                 ▼
                     [ LandingDeploymentEngine ]
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
┌──────────────────┐                            ┌──────────────────┐
│AstroLandingPlugin│                            │NextjsLandingPlugin│
└────────┬─────────┘                            └────────┬─────────┘
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 │
 ┌───────────────────────────────┼───────────────────────────────┐
 ▼                               ▼                               ▼
[Cloudflare Pages Provider]     [Vercel Provider]               [Netlify Provider]
 (Direct Upload / API)           (Deployment API)                (Deploy Webhook)
                                 │
                                 ▼
        [ DeploymentRecord + SHA-256 Fingerprint + Rollback Store ]
                                 │
                                 ▼
                        [ ExperimentLedger ]
```

---

## 🛠️ Ações Disponíveis via Runtime (`execute`)

| Ação (`action`) | Função | Payload de Entrada | Retorno |
|---|---|---|---|
| `build` | Compila os artefatos estáticos e gera o fingerprint SHA-256 | `{"id": "OFFER-1", "title": "Product"}` | Objeto `BuildResult` |
| `deploy` | Publica um build compilado na CDN selecionada | `{"cdn_provider": "cloudflare_pages"}` | Objeto `DeploymentRecord` |
| `build_and_deploy` | Compila e publica em uma única etapa | `{"title": "Product", "cdn_provider": "vercel"}` | `DeploymentRecord` + URL pública |
| `rollback` | Executa o rollback instantâneo para um deploy anterior | `{"deployment_id": "CF-DEP-101"}` | Objeto `RollbackRecord` |

---

## 🔐 Fingerprints SHA-256 e Versionamento SemVer

1. **`build_fingerprint`**: Hash SHA-256 calculado sobre o manifesto e os arquivos compilação, permitindo auditoria matemática.
2. **Versionamento**: Formato `v1.0.0-{framework}-{timestamp}` (ex: `v1.0.0-astro-20260721-030531`).
3. **Rollback Instantâneo**: Desativa o deploy atual (`is_active = False`) e reativa a versão estável selecionada (`is_active = True`).

---

## 🚀 Exemplo de Uso via Runtime

```python
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.landing import LandingPluginFactory

runtime = PluginRuntime()
astro_plugin = LandingPluginFactory.create_astro_plugin()
runtime.register_plugin(astro_plugin)

# Compilação e Deploy Automático
result = astro_plugin.execute({
    "action": "build_and_deploy",
    "id": "OFFER-PROD-100",
    "title": "Curso Master AI",
    "cdn_provider": "cloudflare_pages"
})

print("URL Pública:", result["landing_url"])
print("Version:", result["version"])
print("Fingerprint SHA-256:", result["build_fingerprint"])

# Execução de Rollback se necessário
rollback_res = astro_plugin.execute({
    "action": "rollback",
    "deployment_id": result["deployment"]["deployment_id"]
})
print("Rollback Status:", rollback_res["rollback"]["status"])
```
