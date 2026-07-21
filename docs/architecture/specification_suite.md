# AI Revenue OS — Suíte de Especificações (Specification Suite v2.8)

> **Architecture Freeze**: *Os contratos de API de Plugins, Modelos de Domínio e Registro de Capacidades estão oficialmente Congelados (Imutáveis).*  
> Toda nova funcionalidade deve reutilizar rigorosamente as entidades congeladas e o Event Backbone sem alterar os contratos da plataforma.

---

## 1. Congelamento do Modelo de Domínio (Domain Invariants)

As seguintes 9 entidades principais compõem os agregados centrais do sistema e são imutáveis em termos de hierarquia:

```text
BusinessAsset
  ├── OfferManifest
  ├── RevenueOpportunity
  ├── Genome
  ├── TopicCandidate
  ├── Experiment
  ├── Portfolio
  ├── Decision
  └── Knowledge
```

Nenhuma classe paralela duplicando essas responsabilidades deve ser criada.

---

## 2. Especificação da Plugin API (Imutável 🔒)

Todo plugin deve obrigatoriamente implementar exatamente esta interface:

```python
class BasePlugin(ABC):
    @property
    @abstractmethod
    def plugin_name(self) -> str: pass

    @property
    @abstractmethod
    def category(self) -> str: pass

    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> bool: pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]: pass

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]: pass

    @abstractmethod
    def shutdown(self) -> None: pass
```

### Invariantes de Plugins:
1. Retorno de `health_check()` DEVE conter a chave `"status"` com valor `"HEALTHY"`, `"DEGRADED"` ou `"UNHEALTHY"`.
2. O método `execute()` DEVE lançar exceções tratáveis registradas no log sem derrubar a aplicação.

---

## 3. Função Objetivo do Economic Brain (Fórmula Quantitativa)

O **Economic Brain** otimiza o valor esperado considerando o ganho de conhecimento como um ativo financeiro:

$$\text{Utility} = \text{ExpectedRevenue} - \text{InfraCost} - \text{RiskPenalty} + \text{KnowledgeGain}$$

Onde:
- $\text{KnowledgeGain} = \log_{10}(\text{Observations} + 1) \times \text{ConfidenceDelta} \times 10.0$
- Experimentos que hoje tenham receita neutra ou levemente negativa podem ser aprovados se $\text{KnowledgeGain}$ compensar o custo de aprendizado.
