# Contributing to AI Revenue OS

Primeiro de tudo, obrigado por dedicar seu tempo para contribuir com a nossa máquina! 🎉

## Como Contribuir

### 1. Padrão de Diretórios
Para mantermos a arquitetura limpa:
- `src/agents/`: Lógica pensante (LLMs, Heurísticas, Críticos).
- `src/services/`: Sensores determinísticos (APIs externas, OpenCV, FFprobe).
- `src/config/profiles/`: Configurações parametrizáveis e estáticas sob controle humano (`.toml`).
- `knowledge/`: Dados orgânicos gerados pelo sistema, telemetria (ex: `.jsonl`), memórias estruturadas e patterns. (Tudo daqui deve estar no `.gitignore`).
- `tests/`: Bateria de testes (unit, smoke, integration).

### 2. Estilo de Código (Lint & Format)
Usamos o **Ruff** para linting e o **Black** (compatível com as regras embutidas no Ruff) para formatação.
Antes de fazer um Pull Request, garanta que seu código passe pelo CI:
```bash
ruff check .
ruff format .
```

### 3. Padrão de Commits
Usamos Conventional Commits:
- `feat:` Nova feature (Ex: `feat: add meditation profile`).
- `fix:` Resolução de um bug.
- `docs:` Alterações de documentação.
- `test:` Adição ou ajuste de testes.
- `refactor:` Alterações de código que não mudam a interface.

### 4. Testes Obrigatórios
Nenhum Pull Request será *mergiado* sem que:
- Os **Unit Tests** e **Smoke Tests** rodem 100% no GitHub Actions.
- Mudanças significativas na pipeline exijam aprovação baseada no teste de integração local `test_mpt_adapter_integration.py` (anexar prints de sucesso no PR).
