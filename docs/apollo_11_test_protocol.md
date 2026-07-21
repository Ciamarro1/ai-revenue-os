# AI Revenue OS: Protocolo de Teste E2E (Missão Apollo 11)

Este protocolo define a metodologia e os checkpoints para realizar o primeiro teste de loop econômico fechado e autônomo do AI Revenue OS v0.1-alpha, validando a integração completa entre os cérebros cognitivos/científicos e o braço físico (Execution Layer).

---

## 🎯 1. Objetivo da Missão
Provar empiricamente que a plataforma consegue de forma autônoma:
1. Propor uma nova hipótese de conteúdo (genoma criativo) com base em tendências.
2. Gerar o ativo (mídia do vídeo/imagem) condizente.
3. Passar pelo gate de controle de qualidade e integridade técnica.
4. Enfileirar e publicar o ativo usando o atuador Playwright (Pinterest).
5. Observar e calibar as previsões com base nos dados resultantes.

---

## 🛠️ 2. Configurações e Variáveis de Teste

### Perfil do Experimento (`config/experiment_profile.yaml`):
O teste deve rodar sob o perfil `canary` com as seguintes características:
- **Nicho**: `finance` (Finanças e Renda Passiva).
- **Rede Alvo**: `pinterest` (Modo Orgânico).
- **Baselines**: Alocação de verbas baseada no Multi-Armed Bandit ativo.

### Configuração de APIs e Contas:
- **Sessão Autenticada**: Certifique-se de que os cookies em `config/sessions/pinterest.json` estejam válidos rodando `python scripts/setup_session.py --platform pinterest`.
- **OpenRouter/Gemini API Key**: Necessária para o Vision Fallback do atuador e a Cognitive Engine.
- **Nvidia API Key**: Necessária para geração de imagens (FLUX.1-schnell).

---

## 📋 3. Roteiro Passo a Passo do Teste

```text
 ┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
 │   1. Geração/Criação │ ───> │  2. Fila/Agendamento │ ───> │    3. Execução/Post  │
 └──────────────────────┘      └──────────────────────┘      └──────────────────────┘
            │                                                                   │
            ▼                                                                   ▼
 ┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
 │ 6. Calibração (Fim)  │ <─── │ 5. Coleta Métricas   │ <─── │  4. Espera / Delay   │
 └──────────────────────┘      └──────────────────────┘      └──────────────────────┘
```

### Passo 1: Disparar Geração do Experimento
Execute o pipeline do runner para criar a hipótese e o asset:
```bash
.\venv\Scripts\python -m src.services.experiment_runner --stop-at-state QUALITY_CHECKED
```
*Verificações:*
- O ID do experimento (ex: `EXP-A1B2C3D4`) foi gravado com status `PENDING` na tabela `experiments`.
- Os arquivos foram salvos na pasta `experiments/EXP-A1B2C3D4/`.
- O relatório de qualidade técnica foi aprovado.

### Passo 2: Enfileirar a Publicação
Insira o job na fila SQLite de publicação utilizando o script do runner ou manualmente via CLI:
- O Job deve possuir o status `pending` na tabela `publication_queue`.

### Passo 3: Executar o Queue Worker
Dispare o worker da Execution Layer para processar o job de publicação:
```bash
.\venv\Scripts\python src/execution/queue_worker.py
```
*Verificações:*
- O Playwright abre em modo headless, carrega os cookies, realiza o upload e preenchimento dos metadados.
- **Evidências**: A pasta `experiments/EXP-A1B2C3D4/publication_evidence/` foi criada contendo `publish_success.png` e `publication_evidence.json`.
- O status do Job mudou para `published` no SQLite.

### Passo 4: Espera Operacional (Delay)
- Aguardar o período mínimo de maturação (ex: 24h a 72h para pins orgânicos propagarem).

### Passo 5: Coleta de Métricas e Calibração
Dispare a raspagem das métricas reais do Pinterest e o cálculo científico:
```bash
.\venv\Scripts\python -m src.services.experiment_runner --resume-from-state OBSERVED
```
*Verificações:*
- A tabela `metrics` no SQLite possui as impressões e CTR reais.
- A `Calibration Engine` calculou o viés e atualizou a `Genome Library`.
- O manifesto final `manifest.json` foi gerado e assinado com hashes criptográficos na pasta do experimento.
- O experimento mudou para status `COMPLETED`.

---

## 🚨 4. Critérios de Sucesso e Parada (Gates)
- **Gate 1**: O vídeo gerado pelo MoneyPrinterTurbo deve possuir legendas legíveis e áudio funcional.
- **Gate 2**: O upload via Playwright não deve disparar bloqueios ou CAPTCHAs permanentes. Se ocorrer erro de seletor, o Vision Fallback precisa se recuperar com sucesso.
- **Gate 3**: O banco de dados SQLite (`prod_db.sqlite3`) deve permanecer íntegro e sem travamento de locks concorrentes.
