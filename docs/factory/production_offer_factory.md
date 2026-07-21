# Production Offer Factory Documentation — AI Revenue OS (Sprint O3)

> **Module**: `src/factory/production/`  
> **Class**: `ProductionOfferFactory`  
> **Output Artifact**: `EnrichedOfferManifest` (estende `OfferManifest`)  
> **Determinismo**: 100% Reprodutível via PRNG com semente SHA-256 de identificador  

---

## 🏛️ Arquitetura da Fábrica de Ofertas

A **Production Offer Factory** é o motor que transforma oportunidades cruas (`RevenueOpportunity`, `ResearchOpportunity` ou `AffiliateProduct`) em manifestos de oferta completos, selados e prontos para renderização em qualquer adaptador (Astro, Next.js, MoneyPrinterTurbo, Pinterest Playwright).

```text
       [ RevenueOpportunity / ResearchOpportunity ]
                           │
                           ▼
             [ ProductionOfferFactory ] ── (Seeded Hash PRNG)
                           │
 ┌─────────────────────────┼─────────────────────────┐
 ▼                         ▼                         ▼
[Copy Generators]    [Creative Generators]    [Metadata Generators]
- Headline Generator - Image Prompts (FLUX)  - SEO & Schema.org
- Benefit Generator  - Video Prompts (MPT)   - Landing Metadata
- Pain Points        - Pinterest Metadata    - Analytics Metadata
- CTA & Urgency      - Keywords Generator    - UTM Tracking
                           │
                           ▼
                 [ Enriched OfferManifest ] ── (Cryptographic Signature)
                           │
                           ▼
                  [ ExperimentLedger ]
```

---

## 🛠️ Os 11 Geradores Determinísticos

| # | Gerador | Descrição | Exemplo de Saída |
|---|---|---|---|
| 1 | **Headline Generator** | Ganchos de alta conversão e proposições de valor | *"Descubra Como Dominar Python Com O Método Formação Master AI"* |
| 2 | **Benefit Generator** | Lista de impulsionadores de valor tangíveis | *"Acesso imediato e vitalício ao conteúdo..."* |
| 3 | **Pain Points Generator** | Dores e objeções superadas pela oferta | *"Frustração por tentar aprender sozinho sem metodologia..."* |
| 4 | **CTA Generator** | Botões de ação com urgência e escassez | *"Garantir Minha Vaga Com Desconto Especial"* |
| 5 | **SEO Metadata Generator** | Title, Description, OG Tags e Canonical URLs | `"title": "Formação Master AI — Site Oficial"` |
| 6 | **Keywords Generator** | Palavras-chave primárias e cauda longa | `["python", "formação master ai", "curso python"]` |
| 7 | **Image Prompts Generator** | Prompts fotorrealistas para FLUX.1 / ComfyUI | `{"type": "hero_background", "prompt": "Professional modern..."}` |
| 8 | **Video Prompts Generator** | Roteiros verticais 9:16 para MoneyPrinterTurbo | `{"voiceover_script": "Você também sente dificuldade...", "format": "vertical_9_16"}` |
| 9 | **Landing Metadata Generator** | Estrutura de seções Hero/Features/Pricing/FAQ | `{"theme": "dark_glassmorphism", "hero_section": {...}}` |
| 10 | **Pinterest Metadata Generator** | Título, descrição, hashtags e pasta de Pin | `{"pin_title": "Descubra o Método Formação Master AI 🚀", ...}` |
| 11 | **Analytics Metadata Generator** | Eventos GA4/PostHog e parâmetros UTM | `{"utm_params": {"utm_source": "pinterest", "utm_campaign": "camp_tech"}}` |

---

## 🔐 Selagem e Assinatura Criptográfica

Para garantir auditabilidade EDD:
1. `inputs_hash`: Hash SHA-256 combinando os dados brutos de entrada da oportunidade.
2. `signature_hash`: Hash SHA-256 gerado a partir do manifesto construído.

---

## 🚀 Exemplo de Uso

```python
from src.revenue_os.analytics.opportunity_schemas import RevenueOpportunity
from src.factory.production import ProductionOfferFactory

factory = ProductionOfferFactory()
opp = RevenueOpportunity(
    id="OPP-101",
    marketplace="Hotmart",
    product_name="Formação Master em IA",
    category="tech",
    commission_rate=0.60,
    epc_usd=4.50
)

manifest = factory.create_enriched_manifest(opp)
print("Headline:", manifest.headline)
print("Signature:", manifest.signature_hash)

# Exportar para Astro SSG
astro_props = manifest.to_astro_props()
```
