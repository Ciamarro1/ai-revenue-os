# MANIFESTO E REGISTRO DE PROVIDERS (PROVIDER_MANIFEST.md)

Este guia orienta desenvolvedores sobre como implementar novos adaptadores concretos (**Adapters**), registrá-los no container IoC (**Registry**) e ativá-los dinamicamente via arquivo de configuração manifest (**Capability Manifest**).

---

## 🛠️ 1. Passo a Passo para Criar um Novo Adapter

Para plugar um novo motor de mercado (ex. Weaviate para banco vetorial) ao AI Revenue OS, siga estes passos:

### Passo A: Criar o módulo do Adapter
Crie o arquivo sob `src/adapters/` (ex. `src/adapters/weaviate_memory.py`).

### Passo B: Implementar a Porta Abstrata
Faça com que a classe herde da interface abstrata correspondente declarada em `src/ports/`:

```python
from typing import List, Dict, Any
from src.ports.memory import MemoryPort

class WeaviateMemoryAdapter(MemoryPort):
    def __init__(self, url: str):
        self.url = url
        # Inicializa cliente Weaviate

    def store(self, content: str, memory_type: str, metadata: Dict[str, Any]) -> str:
        # Lógica de gravação física no Weaviate
        return "weaviate-uuid"

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # Lógica de busca vetorial
        return []

    def retrieve_context(self, entity: str, limit: int = 3) -> str:
        # Formata contexto
        return ""
```

---

## 🔌 2. Registro no ProviderRegistry (Inversão de Controle)

O registro do adaptador concreto deve ocorrer no bootstrap de inicialização da aplicação (geralmente orquestrado em `src/runtime/runtime.py`):

```python
from src.ports import ProviderRegistry, Capabilities
from src.adapters.weaviate_memory import WeaviateMemoryAdapter

# 1. Obter instância singleton
registry = ProviderRegistry()

# 2. Instanciar o adaptador concreto com suas configurações
adapter = WeaviateMemoryAdapter(url="http://localhost:8080")

# 3. Registrar o adaptador associando-o ao Enum correspondente
registry.register(Capabilities.MEMORY_SEMANTIC, adapter)
```

---

## 📂 3. Configuração via Capability Manifest File

O Runtime lê o arquivo `capability_manifest.json` localizado na raiz do projeto para determinar quais adapters carregar ativamente de forma declarativa.

### Exemplo de `capability_manifest.json`

```json
{
  "providers": {
    "memory.semantic": {
      "adapter": "weaviate",
      "enabled": true
    },
    "llm.chat": {
      "adapter": "litellm",
      "model": "claude-3-opus",
      "enabled": true
    },
    "browser": {
      "adapter": "playwright",
      "headless": true
    }
  }
}
```

Com isso, a troca de bancos vetoriais, LLMs, barramentos de mensageria ou motores de workflows é realizada de forma declarativa via JSON, sem necessidade de alterar código no cérebro cognitivo do core.
