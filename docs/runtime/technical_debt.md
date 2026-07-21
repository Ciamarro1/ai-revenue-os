# TECHNICAL DEBT (DÍVIDA TÉCNICA)

Lista de refatorações pendentes e fragilidades de software que reduzem a manutenabilidade do sistema.

1. **Abstração de Armazenamento de Arquivos**: Os criativos gerados são armazenados em caminhos locais absolutos. Precisamos de uma camada abstrata de armazenamento para suportar S3/Cloud Storage.
2. **Alertas de Erro**: O sistema registra logs locais sob falhas catastróficas, mas falta notificação via canais externos (ex: Discord/Slack webhooks).
3. **Paralelismo do QueueWorker**: O daemon do `QueueWorker` executa tarefas de forma estritamente serial. Deve ser expandido para suportar threads paralelas limitadas por host.
