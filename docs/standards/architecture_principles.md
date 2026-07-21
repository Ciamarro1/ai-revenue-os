# PRINCÍPIOS DE ARQUITETURA (ARCHITECTURE PRINCIPLES)

Todo componente, classe e módulo do AI Revenue OS deve ser projetado de acordo com os seguintes pilares de arquitetura de software:

---

## Princípio 1: Responsabilidade Única (SRP)
- Cada classe ou arquivo de código deve ter um único motivo para mudar.
- Não misture regras estatísticas, orquestração e código de infraestrutura de rede.
- Classes auxiliares de parsing ou validação devem ser isoladas em utilitários ou subcamadas específicas.

## Princípio 2: Observabilidade Nativa
- Nenhuma operação de rede, alteração estatística de confiança ou decisão orçamentária pode ocorrer de forma silenciosa.
- O código deve instrumentar logs estruturados em níveis adequados (`INFO` para fluxo comum, `WARNING` para cooldowns ou anomalias tratadas, `ERROR`/`CRITICAL` para falhas que ativam o disjuntor).
- Etapas de latência crítica devem utilizar gerenciadores de tempo (`TimingContext`) para monitoramento contínuo.

## Princípio 3: Testabilidade por Design
- O código deve ser escrito facilitando a injeção de dependências ou mocks para permitir testes rápidos e confiáveis.
- Evite construtores internos complexos que instanciam conexões físicas ou sockets. Prefira passar interfaces de dependência injetadas para desacoplamento de testes.

## Princípio 4: Substituibilidade (Interface-Driven Design)
- As camadas centrais devem se comunicar por meio de interfaces ou contratos abstratos (ex: `PublisherBase`), permitindo que a implementação de infraestrutura (como o `pinterest_playwright`) seja inteiramente substituída sem afetar o runner.

## Princípio 5: Configuração Externa e Desacoplada
- Nenhuma lógica operacional do sistema deve depender de constantes locais fixas no código.
- Limites de Trust Score, cooldowns de postagem, número máximo de tentativas de publicação e URLs de conexão devem ser lidos de forma dinâmica a partir de variáveis de ambiente (`.env`) ou tabelas de banco (`system_state`).

## Princípio 6: Desacoplamento da Infraestrutura (Domain Isolation)
- O domínio do negócio (a inteligência científica contida em `revenue_os/analytics/`) não deve conhecer detalhes de bancos de dados específicos, frameworks de automação ou APIs web.
- O mapeamento e a tradução técnica de entrada/saída de dados externos devem ocorrer estritamente na camada de `Adapters`.
