# MODELO DE NEGÓCIOS (BUSINESS MODEL)

O AI Revenue OS opera sob a filosofia de um **Lean Quant Fund** (fundo quantitativo enxuto) aplicado à captura e monetização da atenção digital. 

---

## Mecânica do Modelo de Arbitragem

O negócio baseia-se em **arbitragem de tráfego**:
1. **Aquisição de Atenção**: O sistema cria e publica conteúdos criativos em plataformas de alto alcance orgânico (ex: Pinterest) ou compra tráfego via anúncios pagos.
2. **Monetização**: Direciona os usuários capturados para páginas de destino (landing pages ou ofertas afiliadas) que geram receita.
3. **Métrica de Rentabilidade**:
   \[\text{LTV} > \text{CPA} + \text{Custos de Infraestrutura}\]
   - Onde **LTV** (Lifetime Value) é o faturamento médio por usuário e **CPA** (Custo de Aquisição) é o custo financeiro gasto em anúncios.

---

## As Duas Fases Operacionais

### Fase 🌱: Organic Discovery Mode (Exploração)
* **Objetivo**: Encontrar tendências e validar a taxa de cliques (CTR) de ganchos criativos usando tráfego gratuito.
* **Custo**: Apenas computação local (GPU/tokens de API).
* **Meta**: Identificar criativos "Campeões" (CTR acima do baseline).

### Fase 💰: Paid Scaling Mode (Explotação)
* **Objetivo**: Multiplicar a receita injetando verba real em anúncios exclusivamente nos criativos já validados.
* **Mecanismo de Proteção**: Regras rígidas de *Stop-Loss* gerenciadas pelo `CapitalAllocator`. Se o CPA de um criativo passar do teto rentável, a veiculação é suspensa instantaneamente.
