from typing import Dict, Any, Optional
from src.revenue_os.plugins.base_plugin import BasePlugin
from src.revenue_os.plugins.creatives.providers.flux_provider import FluxImageProvider
from src.revenue_os.plugins.creatives.providers.comfyui_provider import ComfyUIImageProvider
from src.revenue_os.plugins.creatives.job_queue import CreativeJobQueue
from src.revenue_os.plugins.creatives.worker_pool import CreativeWorkerPool
from src.revenue_os.plugins.creatives.models import CreativeJob

class ImageGenerationPlugin(BasePlugin):
    """
    ImageGenerationPlugin (Sprint O5).
    Plugin estendendo BasePlugin SDK para geração e enfileiramento de imagens com FLUX e ComfyUI.
    """

    def __init__(
        self,
        flux_provider: Optional[FluxImageProvider] = None,
        comfyui_provider: Optional[ComfyUIImageProvider] = None,
        queue: Optional[CreativeJobQueue] = None
    ):
        self.flux = flux_provider or FluxImageProvider()
        self.comfyui = comfyui_provider or ComfyUIImageProvider()
        self.queue = queue or CreativeJobQueue()
        self.worker_pool = CreativeWorkerPool(self.queue)
        self._initialized = False

    @property
    def plugin_name(self) -> str:
        return "image_generation_plugin"

    @property
    def category(self) -> str:
        return "image"

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self._initialized else "UNHEALTHY",
            "plugin_name": self.plugin_name,
            "category": self.category,
            "flux_enabled": self.flux.is_enabled,
            "comfyui_enabled": self.comfyui.is_enabled,
            "pending_queue_count": self.queue.pending_count()
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "generate")
        prompt = payload.get("prompt", "Professional digital asset")
        filename = payload.get("filename", "image_output.png")
        priority = payload.get("priority", "MEDIUM")

        if action == "generate":
            # Execução direta com fallback automático FLUX -> ComfyUI
            try:
                asset = self.flux.generate_image(prompt, filename)
                return {"status": "SUCCESS", "action": action, "asset": asset.model_dump()}
            except Exception as e:
                asset = self.comfyui.generate_image(prompt, filename)
                return {"status": "SUCCESS", "action": action, "fallback_used": True, "asset": asset.model_dump()}

        elif action == "enqueue":
            job_id = f"JOB-IMG-{hash(prompt) & 0xffffffff}"
            job = CreativeJob(job_id=job_id, job_type="image", provider_name="flux", prompt=prompt, priority=priority)
            self.queue.enqueue(job)
            return {"status": "SUCCESS", "action": action, "job": job.model_dump()}

        elif action == "process_queue":
            asset = self.worker_pool.process_next_job(
                handler=lambda j: self.flux.generate_image(j.prompt, f"job_{j.job_id}.png"),
                fallback_handler=lambda j: self.comfyui.generate_image(j.prompt, f"job_{j.job_id}_fb.png")
            )
            if asset:
                return {"status": "SUCCESS", "action": action, "asset": asset.model_dump()}
            return {"status": "NO_JOBS", "action": action}

        raise ValueError(f"Ação desconhecida '{action}' para ImageGenerationPlugin")

    def shutdown(self) -> None:
        self._initialized = False
