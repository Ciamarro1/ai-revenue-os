# ARQUITETURA E PADRÕES DE DESIGN

O AI Revenue OS é estruturado sob os princípios de **Clean Architecture**, **Domain-Driven Design (DDD)**, **SOLID** e, quando aplicável, **Hexagonal Architecture** (arquitetura de portas e adaptadores) e **Event-Driven/Queue-Based Processing**.

## Camadas do Sistema

A base de código está organizada em camadas isoladas para garantir desacoplamento e testabilidade:

1. **`src/revenue_os/analytics/` (Motor Científico)**
   - Responsável pelos cálculos de calibração, atribuição de receita, alocação de fundos (Capital Allocator) e tomada de decisão empírica baseada em testes estatísticos (SciPy, testes-T, p-values).
   
2. **`src/revenue_os/observability/` (Auditoria e Snapshots)**
   - Gerencia a rastreabilidade e integridade operacional. Contém o `Decision Ledger` (`decisions.jsonl` append-only) e o `Reality Snapshot` (séries temporais de desvio preditivo).

3. **`src/revenue_os/adapters/` (Camada de Tradução)**
   - Traduz dados de APIs e plataformas externas para os esquemas canônicos estruturados (ex: `RealWorldMetrics`).

4. **`src/revenue_os/core/` (Ponto de Entrada CLI)**
   - Define a linha de comando (`cli.py`) do sistema para gerenciamento manual e setup operacional.

5. **`src/services/` (Orquestração Operacional)**
   - Orquestra os loops de alto nível. O `ExperimentRunner` gerencia o ciclo fechado das hipóteses e experimentos.

6. **`src/factory/` (Geração de Assets & Quality Gates)**
   - Lida com a criação de conteúdo (imagens via NVIDIA API e vídeos via MoneyPrinterTurbo) e passa-os por filtros de controle de qualidade (`VideoQualityGate`/`ImageQualityGate`) e deduplicação perceptual (`ImageDeduplicator`).

7. **`src/reality/` (Interface com o Mundo Físico)**
   - Conectores de baixo nível e raspagem (ex: APIs de redes sociais, browser Playwright/OpenManus).

8. **`src/execution/` (Atuadores Determinísticos)**
   - Lida com a atuação no mundo real através do `QueueWorker` que processa a fila assíncrona (`publication_queue` no SQLite) e executa publicações via Playwright com suporte a `Vision Fallback`.

9. **`src/agents/` (Agentes Cognitivos)**
   - Agentes de IA focados em otimização criativa e refinação cognitiva de ganchos (ex: `Creative Optimizer`).

10. **`src/mcp/` (Internal MCP Registry)**
    - Registro de servidores MCP que servem de interface de ferramentas para os agentes.

---

## Máquina de Estados (Pipeline de 9 Estados)

O ciclo de vida de qualquer hipótese e experimento associado avança de forma assíncrona pelas seguintes fases:

```text
 [CREATED] ➔ [RESEARCHED] ➔ [HYPOTHESIS_FORMED] ➔ [ASSET_GENERATED] ➔ [QUALITY_CHECKED]
                                                                     │
 [CALIBRATED] ⮘ [OBSERVED] ⮘ [PUBLISHED] ⮘ [HUMAN_APPROVED] ⮘────────┘
```

### Estados de Transição e Sucesso:
* **`CREATED`**: O experimento é inicializado e o `ResourceAllocator` escolhe o modo (Exploração ou Explotação).
* **`RESEARCHED`**: Pesquisa automática de nichos e tendências de mercado.
* **`HYPOTHESIS_FORMED`**: Geração de um genoma de conteúdo preditivo estruturado.
* **`ASSET_GENERATED`**: Renderização física das mídias (vídeos e imagens).
* **`QUALITY_CHECKED`**: Validação nos portões de qualidade técnicos e lógicos.
* **`HUMAN_APPROVED`**: Checkpoint Canary para controle operacional de postagem.
* **`PUBLISHED`**: Postagem realizada fisicamente na plataforma.
* **`OBSERVED`**: Coleta de métricas e conversões no mundo físico.
* **`CALIBRATED`**: Análise estatística de erro preditivo e atualização da Genome Library.

### Estados de Falha:
* **`FAILED_RETRYABLE`**: Erro temporário (ex: timeout de rede), permitindo nova tentativa.
* **`FAILED_PERMANENT`**: Falha grave de integridade ou lógica (ex: vídeo corrompido que falha no Quality Gate), bloqueando o ciclo do experimento.
