# ANTIPADRÕES DE CÓDIGO (ANTI-PATTERNS)

Lista exaustiva de padrões e práticas de programação estritamente **proibidos** no AI Revenue OS. Qualquer revisão de código (Reviewer Role) deve rejeitar alterações que contenham estas práticas.

---

## 1. Duplicação de Código (Code Duplication)
* **O que é**: Copiar e colar a mesma lógica de manipulação de mídias, inicialização de Playwright ou consultas SQL em múltiplos scripts.
* **Por que é proibido**: Dificulta a manutenção e correções de segurança. Lógicas repetidas devem ser extraídas para utilitários comuns, adaptadores ou classes bases.

## 2. Invenção de APIs (API Hallucination)
* **O que é**: Chamar parâmetros fictícios ou métodos inexistentes nas APIs do Pinterest, OpenAI, SciPy ou Pydantic com base em alucinações de LLM.
* **Por que é proibido**: Gera falhas silenciosas de execução. Toda chamada externa de API deve estar documentada e confirmada via tipos estritos ou prototipagem no scratch.

## 3. Configurações e Credenciais Hardcoded (Hardcoding)
* **O que é**: Escrever caminhos absolutos locais de arquivos, chaves de API, segredos de cookies ou valores de timeout fixos diretamente nos scripts fonte.
* **Por que é proibido**: Quebra a portabilidade do Docker e gera riscos graves de vazamento de credenciais no repositório público. Use o arquivo `.env` ou a tabela de banco `system_state`.

## 4. Acoplamento Bidirecional e Vazamento de Camadas (High Coupling)
* **O que é**: Importar seletores ou comandos do Playwright/Pinterest (`src/execution/`) dentro das engines estatísticas (`src/revenue_os/analytics/`), ou vice-versa.
* **Por que é proibido**: Viola as regras da Clean Architecture. O motor estatístico deve operar apenas com estruturas canônicas e isoladas das complexidades e flutuações das redes sociais.

## 5. Funções Gigantes (Giant Functions / God Classes)
* **O que é**: Funções, métodos ou classes com mais de 50 a 100 linhas ou que tentam gerenciar múltiplas responsabilidades (ex: renderizar vídeo, salvar cookies, atualizar banco e enviar log no mesmo método).
* **Por que é proibido**: Torna o código ilegível, impossibilita testes unitários eficientes e viola o Princípio da Responsabilidade Única (SRP).

## 6. Dependências Circulares (Circular Imports)
* **O que é**: O Módulo A importa o Módulo B, e o Módulo B importa o Módulo A, gerando problemas de inicialização do interpretador Python.
* **Por que é proibido**: Indica falha no design e na hierarquia de dependências do sistema.

## 7. IA para Lógicas Determinísticas (Cognitive Waste)
* **O que é**: Utilizar LLMs para decidir onde clicar em uma página web estática ou para formatar datas e filtrar tabelas que poderiam ser resolvidos de forma determinística via código Playwright ou SQL.
* **Por que é proibido**: Alto custo de tokens, lentidão desnecessária de processamento e imprevisibilidade no fluxo de execução do sistema.
