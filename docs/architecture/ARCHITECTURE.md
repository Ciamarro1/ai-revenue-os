# ARQUITETURA HEXAGONAL BLUEPRINT (ARCHITECTURE.md)

Este documento descreve as diretrizes de design, fluxo de dependências e regras arquiteturais do **AI Revenue OS**. O sistema adota uma **Arquitetura Hexagonal (Ports & Adapters)** estrita para isolar a inteligência de negócios proprietária de infraestruturas commodity de terceiros.

---

## 📐 1. Fluxo de Dependências

O fluxo de controle e injeção do sistema segue uma direção linear, de fora para dentro no bootstrapping de conexões, e de dentro para fora na resolução de operações:

```text
       [ Runtime / Lifecycle ] (Inicialização e Health Checks)
                 │
                 ▼
       [ Provider Registry ] (IoC Container) ◄─── [ capability_manifest.json ]
                 │
                 ▼
          [ Core Facade ] (CognitiveKernel)
                 │
                 ▼
             [ Ports ] (src/ports/ - Interfaces Abstratas ABC)
                 │
                 ▼
            [ Adapters ] (src/adapters/ - Implementações Concretas)
                 │
                 ▼
     [ Bibliotecas Externas ] (Qdrant, LiteLLM, Temporal, Feast)
```

---

## 📂 2. Estrutura do Namespace (`src/`)

```text
src/
├── core/            # Domínio epistemológico e científico proprietário (Beliefs, Evidence, Decisions).
├── ports/           # Contratos abstratos (Ports), chaves de capacidades (Enums) e container IoC.
├── adapters/        # Adaptadores e conectores técnicos para ferramentas de mercado.
├── integrations/    # Integrações externas de negócio e APIs específicas do domínio (Pinterest).
└── runtime/         # Bootstrap do sistema, configurações de ambiente e saúde operacional.
```

---

## 🔒 3. Diretrizes Invioláveis de Acoplamento

1. **Pureza do Core**: O pacote `src/core/` não importa classes, funções ou variáveis de `src/adapters/`, `src/integrations/` ou de bibliotecas pesadas de terceiros (como `qdrant_client`, `temporalio`, `litellm`, etc.).
2. **Dependência via Portas**: Toda e qualquer infraestrutura física é consumida pelo `core` através de interfaces abstratas declaradas em `src/ports/`.
3. **Resolução de Capacidades (IoC)**: Módulos de decisão resolvem instâncias ativamente por meio do `ProviderRegistry` usando chaves do enum `Capabilities` ou classes Portas.
4. **Isolamento de Configurações**: Configurações específicas de adaptadores (portas de conexão, URLs, tokens) residem exclusivamente nas dataclasses de `src/ports/config.py` e são passadas aos adaptadores no momento de sua criação.
5. **Autonomia de Testes**: A suíte de testes locais deve rodar com sucesso usando adaptadores in-memory ou fallbacks locais sem depender de Docker ativo ou conexões de rede externas.
