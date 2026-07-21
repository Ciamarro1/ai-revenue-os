# AI Revenue OS — Diretriz Arquitetural: Open Source First

> **Princípio Fundamental**: *Open Source First. Build Only the Differentiator.*  
> Nunca desenvolver o que já existe e é maduro na comunidade Open Source. Desenvolver estritamente a inteligência decisória e a vantagem competitiva do fundo.

---

## 📜 Regras Invioláveis de Integração

### Princípio #1 — Orquestração sobre Reinvenção
O **AI Revenue OS** não compete com ferramentas Open Source ou plataformas existentes. Ele atua como o **Motor Cognitivo e Cérebro de Orquestração**, conectando e tomando decisões sobre essas ferramentas.

### Princípio #2 — A Revisão Open Source Obrigatória (Open Source Review)
Antes de escrever qualquer nova funcionalidade ou módulo no sistema, a equipe (ou agente autônomo) deve responder à seguinte pergunta obrigatória:

> **"Existe um projeto Open Source maduro que resolve 80% do problema?"**
> - **SIM** ➔ Integrar via adaptador/porta, acoplar e reutilizar.
> - **NÃO** ➔ Construir apenas a camada proprietária de decisão.

### Princípio #3 — Isolamento da Lógica Proprietária
O código proprietário do AI Revenue OS deve concentrar-se exclusivamente na **Inteligência de Decisão e Aprendizado Contínuo**. Todo componente de infraestrutura (CMS, navegadores, bancos de dados, dashboards) deve ser modular e totalmente substituível.

---

## 🎯 Divisão Estrita de Responsabilidades

### O QUE CONSTRUIR DO ZERO (Vantagem Competitiva Proprietária 🧠)
Estes componentes constituem a propriedade intelectual e o diferencial competitivo do fundo:

1. **Genome Library**: Biblioteca evolutiva de genomas criativos e cálculo de *Genome Score*.
2. **Knowledge Flywheel**: Motor de aprendizado contínuo e retroalimentação ex-post.
3. **Economic Brain**: Cérebro econômico de previsão financeira sob incerteza.
4. **Portfolio Manager**: Alocação quantitativa de recursos (Knapsack) e *Experiment Killer* (stop-loss).
5. **Experiment Runner**: Máquina de estados determinística de 9 fases.
6. **Decision Engine & Ledger**: Log auditável e explicabilidade de decisões financeiras.
7. **Opportunity Engine**: Descoberta e ranking de `RevenueOpportunity`.
8. **Self-Optimization Engine**: Diagnóstico interno de gargalos e auto-otimização do runtime.

---

### O QUE NUNCA CONSTRUIR DO ZERO (Reaproveitamento Open Source 📦)
Estes componentes utilizam soluções Open Source e serviços maduros da indústria:

| Categoria | Solução Open Source Homologada | Função no AI Revenue OS |
| --- | --- | --- |
| **Landing Pages & CMS** | Astro / Next.js / Hugo / Headless WordPress | Renderização de páginas de alta velocidade e SEO |
| **Workflow & Automação** | n8n / Activepieces / Windmill / Temporal | Automação de fluxos secundários e rotinas batch |
| **Browser Automation** | Playwright / Chromium | Atuação física em redes sociais e scraping |
| **AI Agents & Frameworks** | PydanticAI / LangGraph / CrewAI | Modelagem estruturada e orquestração de agentes |
| **Modelos de Linguagem** | Gemini / OpenAI / Anthropic / DeepSeek / Ollama | Inferência de linguagem e visão sem treinamento local |
| **RAG & Vector Search** | Qdrant / Chroma / LlamaIndex / Haystack | Armazenamento e busca vetorial de conhecimento |
| **Dashboards & Analytics** | Grafana / Metabase / Apache Superset | Visualização de métricas e dashboards analíticos |
| **Bancos de Dados** | SQLite / PostgreSQL / Redis / ClickHouse | Persistência relacional, chave-valor e analítica OLAP |
| **Busca Indexada** | Meilisearch / Typesense | Indexação rápida de catálogos e tópicos |
| **Fila & Mensageria** | Redis Streams / RabbitMQ / Celery | Fila de tarefas assíncronas |
| **Object Storage** | MinIO (S3 Compatible) | Armazenamento de mídias e renders finais |

---

## 📁 Estrutura de Encapsulamento

```text
AI Revenue OS
├── Brain (Proprietário - Decisão, Genomas, Portfolio, Flywheel)
├── Orchestration (Proprietário - ExperimentRunner, SkillEngine)
├── Connectors (Proprietário - Adaptadores de Plataformas)
└── OSS Catalog (Integrations - Catálogo e encapsulamento de soluções Open Source)
```
