# PADRÕES DE DESIGN APROVADOS (DESIGN PATTERNS)

Para manter a consistência técnica em toda a base de código, os seguintes padrões de projeto (Design Patterns) são os únicos homologados para uso no AI Revenue OS:

---

## 1. Strategy (Estratégia)
* **Objetivo**: Escolher dinamicamente o provedor de tendências ou a rede de destino.
* **Uso**: O `TrendProvider` ou os geradores de imagens podem alterar seu motor interno (ex: FLUX.1 vs. outros modelos) com base em chaves de configuração, utilizando a mesma interface abstrata.

## 2. Factory (Fábrica)
* **Objetivo**: Instanciar publicadores ou geradores específicos de plataforma de forma encapsulada.
* **Uso**: A criação de conexões e workers baseia-se em parâmetros (ex: instanciar `PinterestPublisher` se a rede alvo for `pinterest`), mantendo a lógica de criação isolada da execução.

## 3. Repository (Repositório)
* **Objetivo**: Desacoplar a lógica de negócio do banco de dados físico.
* **Uso**: O `HypothesisRegistry` e o `ExperimentRegistry` abstraem as queries SQLite cruas, expondo métodos limpos (`get_by_id`, `update_status`, `add_metric`) de forma relacional.

## 4. Observer (Observador)
* **Objetivo**: Reagir a mudanças de estado ou métricas críticas de infraestrutura.
* **Uso**: Emissores de eventos notificam o disjuntor de segurança sempre que ocorrem falhas operacionais seguidas de degradação do Trust Score.

## 5. Pipeline / Chain of Responsibility (Cadeia de Processamento)
* **Objetivo**: Executar transformações e validações sequenciais em ativos de mídia.
* **Uso**: Os arquivos gerados passam em sequência pelo `ImageDeduplicator`, `ImageQualityGate` e depois pelo lacrador de manifesto, onde cada etapa pode interromper o fluxo se detectar inconsistências.

## 6. State Machine (Máquina de Estados)
* **Objetivo**: Controlar o ciclo de vida rigoroso de transições dos experimentos.
* **Uso**: O `ExperimentRunner` gerencia a transição de experimentos através dos 9 estados canônicos (`CREATED` -> `RESEARCHED` -> ... -> `CALIBRATED`). Transições ilegais (ex: ir de `CREATED` direto para `PUBLISHED`) são travadas e disparam exceções.

## 7. Circuit Breaker (Disjuntor)
* **Objetivo**: Proteger a saúde e os recursos financeiros do sistema sob falhas catastróficas.
* **Uso**: O circuito de proteção monitora a integridade de rede, banco e disco. Caso o Health Score caia, ele "abre" o disjuntor (ativando a flag global `AUTOPAUSE` no SQLite), travando as operações de publicação até que o estado se reestabeleça.
