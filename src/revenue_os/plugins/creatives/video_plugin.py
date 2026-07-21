from typing import Dict, Any, Optional
from src.revenue_os.plugins.base_plugin import BasePlugin
from src.revenue_os.plugins.creatives.providers.mpt_provider import MoneyPrinterTurboVideoProvider
from src.revenue_os.plugins.creatives.providers.remotion_provider import RemotionVideoProvider
from src.revenue_os.plugins.creatives.job_queue import CreativeJobQueue
from src.revenue_os.plugins.creatives.worker_pool import CreativeWorkerPool
from src.revenue_os.plugins.creatives.models import CreativeJob

class VideoGenerationPlugin(BasePlugin):
    """
    VideoGenerationPlugin (Sprint O5).
    Plugin estendendo BasePlugin SDK para geração e enfileiramento de vídeos verticais 9:16 com MPT e Remotion.
    """

    def __init__(
        self,
        mpt_provider: Optional[MoneyPrinterTurboVideoProvider] = None,
        remotion_provider: Optional[RemotionVideoProvider] = None,
        queue: Optional[CreativeJobQueue] = None
    ):
        self.mpt = mpt_provider or MoneyPrinterTurboVideoProvider()
        self.remotion = remotion_provider or RemotionVideoProvider()
        self.queue = queue or CreativeJobQueue()
        self.worker_pool = CreativeWorkerPool(self.queue)
        self._initialized = False

    @property
    def plugin_name(self) -> str:
        return "video_generation_plugin"

    @property
    def category(self) -> str:
        return "video"

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self._initialized else "UNHEALTHY",
            "plugin_name": self.plugin_name,
            "category": self.category,
            "mpt_enabled": self.mpt.is_enabled,
            "remotion_enabled": self.remotion.is_enabled,
            "pending_queue_count": self.queue.pending_count()
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "generate")
        prompt = payload.get("prompt", "Vertical promotional video script")
        filename = payload.get("filename", "video_output.mp4")
        priority = payload.get("priority", "MEDIUM")

        if action == "generate":
            try:
                asset = self.mpt.generate_video(prompt, filename)
                return {"status": "SUCCESS", "action": action, "asset": asset.model_dump()}
            except Exception as e:
                asset = self.remotion.generate_video(prompt, filename)
                return {"status": "SUCCESS", "action": action, "fallback_used": True, "asset": asset.model_dump()}

        elif action == "enqueue":
            job_id = f"JOB-VID-{hash(prompt) & 0xffffffff}"
            job = CreativeJob(job_id=job_id, job_type="video", provider_name="money_printer_turbo", prompt=prompt, priority=priority)
            self.queue.enqueue(job)
            return {"status": "SUCCESS", "action": action, "job": job.model_dump()}

        elif action == "process_queue":
            asset = self.worker_pool.process_next_job(
                handler=lambda j: self.mpt.generate_video(j.prompt, f"job_{j.job_id}.mp4"),
                fallback_handler=lambda j: self.remotion.generate_video(j.prompt, f"job_{j.job_id}_fb.mp4")
            )
            if asset:
                return {"status": "SUCCESS", "action": action, "asset": asset.model_dump()}
            return {"status": "NO_JOBS", "action": action}

        raise ValueError(f"Ação desconhecida '{action}' para VideoGenerationPlugin")

    def shutdown(self) -> None:
        self._initialized = False
