# Sprint 7.2 - Skill Engine Readiness Gate

Este documento apresenta a auditoria de prontidão e validação técnica da **Sprint 7.2 (Skill Engine)** para garantir que o sistema está preparado para avançar para a **Sprint 7.5 (Market Intelligence & Autonomous Operation)**.

---

## 1. Mapeamento das 5 Skills Funcionais

Para cada uma das 5 habilidades de negócio semeadas no `SkillRegistryService`, detalhamos abaixo a estrutura de capacidades, ferramentas reais associadas, adapters e fluxo de dados.

### A) `market_research_skill`
* **Objetivo de Negócio**: Pesquisar e enriquecer oportunidades de mercado.
* **Passos e Capabilities Utilizadas**:
  1. `Search`
  2. `Document processing`
  3. `Evidence creation`
  4. `Opportunity enrichment`
* **Tools Reais Executadas**: Nenhuma (utiliza tool de fallback `System Provider` gerada dinamicamente).
* **Adapter Chamado**: Nenhum (mockado localmente nos handlers padrão do serviço).
* **Dados de Entrada**: `{"niche": "home organization", "channel": "pinterest"}`
* **Dados de Saída**: `{"niche": "home organization", "channel": "pinterest", "search_results": "...", "processed_data": "...", "evidence_id": 42, "opportunity_id": 100}`
* **Eventos Emitidos**: `SkillStarted`, `SkillStepCompleted` (x4), `SkillCompleted` (ou `SkillFailed`).

### B) `generate_creative_assets_skill`
* **Objetivo de Negócio**: Produzir e validar criativos de imagem/vídeo.
* **Passos e Capabilities Utilizadas**:
  1. `Creative prompt generation`
  2. `Image/video provider`
  3. `Asset registration`
  4. `Quality validation`
* **Tools Reais Executadas**: Nenhuma (utiliza tool de fallback `System Provider`).
* **Adapter Chamado**: Nenhum (não chama o Flux Adapter real nem o repositório de assets).
* **Dados de Entrada**: `{"niche": "home organization"}`
* **Dados de Saída**: `{"niche": "home organization", "creative_prompt": "...", "media_path": null, "approved_title": null, "approved_description": null, "asset_registered": true, "valid": true}` *(Nota: media_path e metadados retornam null devido a bug no mapeamento de saída)*.
* **Eventos Emitidos**: `SkillStarted`, `SkillStepCompleted` (x4), `SkillCompleted` (ou `SkillFailed`).

### C) `quality_validation_skill`
* **Objetivo de Negócio**: Aplicar ganchos físicos e lógicos de validação de qualidade sobre os ativos.
* **Passos e Capabilities Utilizadas**:
  1. `Asset loading`
  2. `Quality checks`
  3. `Score calculation`
  4. `Approve/reject`
* **Tools Reais Executadas**: Nenhuma (utiliza tool de fallback `System Provider`).
* **Adapter Chamado**: Chamada lógica interna para `ImageQualityGate` e `VideoQualityGate`.
* **Dados de Entrada**: `{"media_path": "temp_val_creative.png"}`
* **Dados de Saída**: Falha fatal de validação no primeiro passo.
* **Eventos Emitidos**: `SkillStarted`, `SkillFailed`.

### D) `publish_distribution_skill`
* **Objetivo de Negócio**: Enfileirar e despachar publicações físicas para redes sociais.
* **Passos e Capabilities Utilizadas**:
  1. `Approved asset loading`
  2. `Publication Queueing`
  3. `Publisher Adapter invocation`
  4. `Publication Event emission`
* **Tools Reais Executadas**: Nenhuma (utiliza tool de fallback `System Provider`).
* **Adapter Chamado**: Nenhum (não invoca a `PublicationQueue` nem o `PinterestPlaywright` real).
* **Dados de Entrada**: `{"media_path": "temp_val_creative.png", "board": "Home Ideas"}`
* **Dados de Saída**: `{"media_path": "temp_val_creative.png", "board": "Home Ideas", "approved_asset": {...}, "job_id": 1001, "published_url": "https://pinterest.com/pin/1001", "event_emitted": true}`
* **Eventos Emitidos**: `SkillStarted`, `SkillStepCompleted` (x4), `SkillCompleted`.

### E) `experiment_analysis_skill`
* **Objetivo de Negócio**: Coletar métricas, gerar reflexões e calibrar crenças.
* **Passos e Capabilities Utilizadas**:
  1. `Observation metrics retrieval`
  2. `Metrics aggregation`
  3. `Reflection generation`
  4. `Belief updating`
* **Tools Reais Executadas**: Nenhuma (utiliza tool de fallback `System Provider`).
* **Adapter Chamado**: Nenhum (não consulta banco real nem invoca a `BeliefAPI` / `BeliefManager` para calibrar crenças de verdade).
* **Dados de Entrada**: `{"experiment_id": "EXP-TEST-001"}`
* **Dados de Saída**: `{"experiment_id": "EXP-TEST-001", "metrics": {...}, "metric_value": 0.05, "reflection_id": 55, "belief_revised": true}`
* **Eventos Emitidos**: `SkillStarted`, `SkillStepCompleted` (x4), `SkillCompleted`.

---

## 2. Resultados do Dry-Run Completo e Diagnóstico

Ao executar uma simulação em memória das habilidades de forma integrada, o diagnóstico revelou que **o motor funciona estruturalmente (a orquestração, transições de estado, retentativas e persistência de telemetry funcionam perfeitamente)**, mas a validação física falhou nos seguintes pontos críticos:

1. **`quality_validation_skill` quebrou de forma fatal**:
   ```
   Falha no passo 1 após 1 tentativas: 3 validation errors for GeneratedAsset
   resolution
     Field required [type=missing, input_value={'path': 'temp_val_creative.png', ...}, input_type=dict]
   provider
     Field required [type=missing, input_value={'path': 'temp_val_creative.png', ...}, input_type=dict]
   confidence
     Field required [type=missing, input_value={'path': 'temp_val_creative.png', ...}, input_type=dict]
   ```
   * **Causa**: O handler simulado `asset_loading_handler` instancia `GeneratedAsset` fornecendo apenas os campos `path`, `approved_title`, `approved_description` e `duration` (este último como float, enquanto o tipo correto é int). Os campos obrigatórios `resolution`, `provider` e `confidence` definidos pelo Pydantic em `src/factory/schemas.py` foram omitidos.

2. **Perda de Dados no Encadeamento (Retorno `null` nos outputs da Skill 2)**:
   * A skill de geração de criativos retorna `media_path`, `approved_title` e `approved_description` com valor `null` no dicionário final de contexto.
   * **Causa**: Um bug de lógica no parser de mapeamento de outputs no `SkillRegistryService.execute_skill` (linhas 208-210):
     ```python
     elif isinstance(step_res, dict) and v.startswith("$.result."):
         res_key = v[9:]
         context[k] = step_res.get(res_key)
     ```
     O retorno real da execução da ferramenta `step_res` é envolto pela estrutura do `ToolRegistryService` sob a chave `"result"`. Ou seja, o dicionário tem a forma `{"result": {"media_path": "...", "approved_title": "..."}}`.
     Ao buscar diretamente na raiz de `step_res` através de `step_res.get("media_path")`, o valor retornado é `None` (deveria acessar `step_res.get("result", {}).get(res_key)`).

---

## 3. Identificação de Mocks, Placeholders e Gaps

A análise de integração direta constatou os seguintes componentes simulados:

| Skill | Componente Simulado (Mock) | Componente Real Disponível no Sistema | Gap / Ação Necessária para Produção |
| :--- | :--- | :--- | :--- |
| **Market Research** | Handlers de busca e enriquecimento de oportunidade retornam dados estáticos. | `src/core/cognition/evidence_engine.py`<br>`src/core/cognition/strategy_repository.py` | Conectar os handlers com o repositório cognitivo real para gravar a `Opportunity` e `Evidence` no SQLite de produção. |
| **Creative Assets** | Geração e validação de imagens salvam arquivos estáticos locais contendo texto fictício. | Factory Layer (`src/factory/image/nvidia/` ou Flux) e `AssetRepository` | Chamar o pipeline de geração de imagem física real e registrar a hash no repositório de assets. |
| **Quality Validation** | Carga física do asset gera uma entidade fictícia com dados incompletos. | `src/factory/quality/image_gate.py`<br>`src/factory/quality/video_gate.py` | Alimentar o validador com instâncias reais geradas pela Factory Layer de produção. |
| **Publish Distribution** | Enfileiramento e publicação de Pinterest retornam URLs estáticas. | `src/execution/queue_worker.py`<br>`src/execution/publisher/pinterest_playwright.py` | Integrar o handler com a `PublicationQueue` e despachar a tarefa para o worker do Playwright. |
| **Experiment Analysis** | Agregação de métricas e calibragem de crenças são representadas por retornos simulados. | `src/reality/social/pinterest/analytics.py`<br>`src/core/cognition/belief_service.py` | Consultar as métricas de performance reais e rodar o loop de revisão Bayesiana com a `BeliefAPI`. |

---

## 4. Blockers Críticos para a Sprint 7.5

Para iniciar com segurança a Sprint 7.5 (Market Intelligence), os seguintes blockers técnicos devem ser resolvidos:

1. **[BLOCKER 1] Falha Fatal de Validação de Asset (Pydantic)**:
   * Ajustar o mock `asset_loading_handler` para instanciar a entidade `GeneratedAsset` com dados em conformidade com o schema Pydantic (especificar `resolution="1080x1920"`, `provider="Nvidia/Flux"`, `confidence=0.95` e `duration` como inteiro).
2. **[BLOCKER 2] Mapeador de Output Bugado (`$.result.*`)**:
   * Ajustar a lógica de parse do `SkillRegistryService` para extrair os dados de dentro da chave `"result"` quando a expressão for `$.result.campo`.
3. **[BLOCKER 3] Ausência de Adapters de Produção Ligados às Habilidades**:
   * As skills no bootstrap padrão estão rodando de forma 100% desconectada dos adaptadores e módulos reais existentes no projeto (ex: `pinterest_playwright.py`, `evidence_engine.py`, `belief_service.py`).
