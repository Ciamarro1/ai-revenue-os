# Creative Generation Engine Documentation — AI Revenue OS (Sprint O5)

> **Plugins**: `image_generation_plugin`, `video_generation_plugin`  
> **Category**: `image`, `video`  
> **SDK Status**: Estendem `BasePlugin` (`src/revenue_os/plugins/base_plugin.py`)  
> **Certification Status**: `PRODUCTION` / `STABLE` 🏅  

---

## 🏛️ Arquitetura da Fábrica Criativa

A **Sprint O5 — Creative Generation Engine** fornece uma infraestrutura desacoplada, assíncrona e resiliente para a produção de imagens (FLUX.1 e ComfyUI) e vídeos verticais 9:16 (MoneyPrinterTurbo e Remotion).

```text
               [ EnrichedOfferManifest (Sprint O3) ]
                                 │
                                 ▼
                     [ CreativeJobQueue (P1/P2/P3) ]
                                 │
                     [ CreativeWorkerPool ]
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
┌──────────────────┐                            ┌──────────────────┐
│  Image Engine    │                            │   Video Engine   │
└────────┬─────────┘                            └────────┬─────────┘
         │                                               │
 ┌───────┴───────┐                               ┌───────┴───────┐
 ▼               ▼                               ▼               ▼
[FLUX.1 Provider][ComfyUI Provider]             [MPT Provider]  [Remotion Provider]
         │               │                               │               │
         └───────┬───────┘                               └───────┬───────┘
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         │
                                         ▼
                     [ StorageManager (storage/creatives/) ]
                                         │
                                 (SHA-256 Hashes)
                                         │
                                         ▼
                               [ ExperimentLedger ]
```

---

## 🛠️ Provedores de Mídia Integrados

| Provedor | Tipo | Modalidade | Descrição |
|---|---|---|---|
| **FLUX.1-schnell / dev** | Imagem | Static Render | API NVIDIA NIMs / Black Forest Labs para imagens ultra-fotorrealistas |
| **ComfyUI Image** | Imagem | Workflow API | API local/remota para geração flexível por nós e controle de difusão |
| **MoneyPrinterTurbo** | Vídeo | Vertical 9:16 | Síntese de vídeo vertical completo com roteiro, voiceover, b-roll e legendas |
| **Remotion Video** | Vídeo | Code-based | Composição gráfica e motion design via React/TypeScript |

---

## ⚙️ Fila Assíncrona, Workers e Fallback

1. **`CreativeJobQueue`**: Fila de prioridades (`HIGH`, `MEDIUM`, `LOW`) com acompanhamento dos estados `QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`.
2. **`CreativeWorkerPool`**: Execução assíncrona em background com estratégias de repetição.
3. **Failover Gracioso**: Caso o provedor primário (ex: FLUX) apresente timeout ou erro de quota, o sistema chaveia automaticamente para o provedor secundário (ex: ComfyUI).
4. **Armazenamento e Hashes**: Ativos são salvos fisicamente em `storage/creatives/{images,videos}/`, catalogados por hash SHA-256 de conteúdo e versionados (`v1.0.0-img-{timestamp}`).

---

## 🚀 Como Utilizar via Runtime

```python
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.creatives import CreativePluginFactory

runtime = PluginRuntime()
img_plugin = CreativePluginFactory.create_image_plugin()
vid_plugin = CreativePluginFactory.create_video_plugin()

runtime.register_plugin(img_plugin)
runtime.register_plugin(vid_plugin)

# Geração Direta de Imagem
img_res = img_plugin.execute({
    "action": "generate",
    "prompt": "Professional 3D mockup box for Formação Master AI",
    "filename": "mockup_ai.png"
})
print("Imagem Gerada SHA-256:", img_res["asset"]["content_hash"])

# Geração Direta de Vídeo 9:16
vid_res = vid_plugin.execute({
    "action": "generate",
    "prompt": "Script promocional sobre finanças",
    "filename": "promo_finance.mp4"
})
print("Vídeo Gerado SHA-256:", vid_res["asset"]["content_hash"])

# Benchmark da Fábrica
bench_engine = CreativePluginFactory.create_benchmark_engine()
bench_res = bench_engine.run_benchmark(lambda: img_plugin.execute({"action": "generate", "prompt": "bench"}))
print("Throughput (jobs/sec):", bench_res.throughput_jobs_per_sec)
```
