# PROTOCOLO DE AVALIAÇÃO (EVALUATION PROTOCOL)

Não basta apenas implementar e rodar código; toda alteração deve ser testada e medida contra baselines de qualidade e performance. Este documento descreve as diretrizes para execução do pipeline de avaliação (evaluation pipeline).

---

## 1. Suite de Testes Técnicos e Regressão

* **Frequência**: Os testes devem ser rodados a cada mudança de código antes do commit.
* **Comando de Validação**:
  ```powershell
  .\venv\Scripts\python -m pytest tests/unit -v
  ```
* **Critério de Aceitação**: 100% dos testes devem estar verdes. Qualquer warning introduzido deve ser analisado e corrigido se indicar depreciação de tipos.

---

## 2. Validação Estatística e Prevenção de Drift

Sob alterações na `Calibration Engine` ou no `MetricsEngine`:
- Roda-se o programa de validação (`test_validation_program.py`) para confirmar que o erro de calibração converge ao longo do tempo.
- **Drift Check**: Garanta que o desvio de calibração (`Calibration Error`) sob dados de simulação não sofra drift de média estatística (desvio contínuo e progressivo no tempo), o que indicaria que a IA está subestimando ou superestimando consistentemente os resultados reais de postagem.

---

## 3. Avaliação de Performance de Infraestrutura (Performance Gates)

Para monitorar gargalos introduzidos na Execution Layer:
* **Mapeamento de Tempos**: Verifique se as novas etapas de upload ou renderização de mídias estão encapsuladas em logs do `TimingContext`.
* **Tolerâncias de Tempo**:
  - Geração de Imagem (FLUX.1-schnell): Máximo 15 segundos por imagem.
  - Renderização de Vídeo (MoneyPrinterTurbo): Máximo 3 minutos por vídeo de 30s.
  - Login e Upload Playwright: Máximo 90 segundos por postagem.
  Se o tempo de processamento cruzar esses limites em simulações controladas, a tarefa deve ser enviada para otimização de performance.

---

## 4. Auditoria de Decisões Algorítmicas
- Verifique se as decisões tomadas por novos fluxos de teste A/B gravam dados interpretáveis na tabela `decisions_ledger` e no arquivo `decisions.jsonl`.
- Logs de auditoria devem justificar estatisticamente por que uma variante foi promovida (ex: CTR > baseline e p-value < 0.05).
