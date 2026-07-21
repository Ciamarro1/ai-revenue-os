# PADRÕES DE PROMPT (PROMPT PATTERNS)

Diretrizes estruturadas para a criação, refinamento e execução de prompts utilizados pelos agentes cognitivos do AI Revenue OS.

---

## 1. Princípios de Engenharia de Prompt

1. **Separação de Contexto (Context Isolation)**:
   - Instruções, regras invioláveis e dados de entrada (como tendências de mercado ou relatórios de performance) devem ser passados em tags XML separadas e claramente identificadas (ex: `<RULES>`, `<CONTEXT>`, `<DATA>`).
2. **Especificação de Papel (Role-Playing)**:
   - Defina sempre um papel específico com competências explícitas (ex: "Você é o Creative Critic do Pinterest...").
3. **Evitar Alucinações (Few-Shot Prompting)**:
   - Forneça exemplos reais estruturados em JSON de entradas e saídas esperadas, demonstrando o comportamento correto.
4. **Instruções Negativas (Negative Guardrails)**:
   - Diga explicitamente o que a IA **NÃO** deve fazer (ex: "Nunca crie ganchos baseados em tópicos médicos ou financeiros não validados").

---

## 2. Estrutura Canônica de Prompt para Agentes

Todo prompt de agente cognitivo deve seguir o seguinte template estrutural:

```text
# ROLE
[Definição clara da identidade e do papel do agente]

# OBJECTIVE
[Qual é o resultado esperado desta execução de prompt]

# SYSTEM CONTEXT (RAG)
As informações abaixo contêm o estado atual e conhecimento relevante recuperado do banco de dados/repositório:
<CONTEXT>
{knowledge_data}
</CONTEXT>

# CONSTRAINTS (GUARDRAILS)
- Nunca invente informações que não estejam no CONTEXT.
- Mantenha a saída no formato estrito especificado em OUTPUT_FORMAT.
[Outras restrições de negócio]

# EXAMPLES
Exemplos de entrada/saída válidos para referência:
<EXAMPLES>
[Entrada de exemplo -> Saída JSON de exemplo]
</EXAMPLES>

# INPUT
Dados da execução corrente:
<INPUT>
{current_input_data}
</INPUT>

# OUTPUT FORMAT
A resposta deve ser obrigatoriamente um objeto JSON válido, sem tags markdown adicionais (como ```json):
{schema_pydantic}
```

---

## 3. Padrões de RAG (Retrieval-Augmented Generation)

* **Busca Semântica vs Causal**:
  - Para busca de ideias de ganchos criativos, use embeddings de proximidade semântica na Genome Library.
  - Para busca de regras arquiteturais ou financeiras, use consulta direta estruturada (SQLite ou arquivos locais) para evitar que o modelo use referências desatualizadas.
* **Tamanho de Janela**:
  - Evite sobrecarregar o contexto do modelo com históricos inteiros de conversas. Summarize logs anteriores e envie apenas snapshots limpos dos dados.
