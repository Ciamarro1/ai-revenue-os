# POLÍTICA DE DEPENDÊNCIAS (DEPENDENCY POLICY)

Para garantir estabilidade, segurança e portabilidade, a introdução de bibliotecas externas de terceiros no AI Revenue OS é rigidamente controlada por este documento.

---

## 1. Critérios para Adicionar Novas Dependências

Qualquer nova biblioteca a ser instalada deve passar pela aprovação do Chief Cognitive Engineer com base nos seguintes requisitos:

1. **Inexistência de Alternativa Nativa**: Só adicione uma biblioteca se a funcionalidade for excessivamente complexa para ser escrita com os pacotes padrão do Python (ex: `math`, `json`, `datetime`) ou com as bibliotecas principais já instaladas (ex: `scipy`, `pydantic`, `playwright`).
2. **Uso Consolidado e Reputação**: A biblioteca deve ser amplamente mantida, possuir documentação ativa e apresentar baixa ocorrência de vulnerabilidades de segurança conhecidas.
3. **Compatibilidade de Licença**: O pacote deve usar licenças permissivas adequadas (como MIT, Apache 2.0, BSD). **Nunca** introduza dependências com licenças restritivas ou virais (ex: GPL v3) que possam afetar a propriedade do projeto.
4. **Impacto no Build**: Não introduza pacotes pesados ou com dependências nativas complexas de compilador C++ que possam quebrar a portabilidade da instalação do repositório no Windows ou Linux (Docker).

---

## 2. Processo de Alteração de Pacotes

* **Local de Registro**: Toda dependência deve ser declarada no arquivo [pyproject.toml](file:///c:/Users/WDAGUtilityAccount/Downloads/projeto/pyproject.toml) na seção correspondente (dependências centrais vs. dependências extras de desenvolvimento `[dev]`).
* **Instalação Local**:
  Após alterar o `pyproject.toml`, o ambiente virtual local deve ser atualizado com:
  ```powershell
  .\venv\Scripts\python -m pip install -e ".[dev]"
  ```

---

## 3. Política de Atualização e Descarte

* **Segurança**: Dependências com vulnerabilidades críticas conhecidas expostas por scanners de segurança devem ser atualizadas imediatamente.
* **Depreciações**: Sempre que uma biblioteca lançar versões estáveis novas, verifique se a suite de testes unitários do pytest permanece verde antes de alterar a versão no `pyproject.toml`.
* **Remoção de Código Morto**: Mapeie regularmente o codebase para remover dependências órfãs que deixaram de ser utilizadas após refatorações.
