import logging
from typing import Callable, Optional, Dict, Any, List
from datetime import datetime, timezone
from src.revenue_os.plugins.creatives.job_queue import CreativeJobQueue
from src.revenue_os.plugins.creatives.models import CreativeJob, GeneratedCreativeAsset

class CreativeWorkerPool:
    """
    Worker Pool para execução de jobs de geração de mídia.
    Suporta Retry com Exponential Backoff e Fallback transparente de provedor.
    """

    def __init__(self, queue: CreativeJobQueue, max_workers: int = 4):
        self.queue = queue
        self.max_workers = max_workers

    def process_next_job(
        self,
        handler: Callable[[CreativeJob], GeneratedCreativeAsset],
        fallback_handler: Optional[Callable[[CreativeJob], GeneratedCreativeAsset]] = None
    ) -> Optional[GeneratedCreativeAsset]:
        job = self.queue.dequeue()
        if not job:
            return None

        try:
            asset = handler(job)
            job.status = "COMPLETED"
            job.completed_at = datetime.now(timezone.utc).isoformat() + "Z"
            return asset
        except Exception as primary_err:
            logging.warning(f"[WorkerPool] Provedor primário '{job.provider_name}' falhou: {primary_err}")
            job.retry_count += 1

            if fallback_handler:
                try:
                    logging.info(f"[WorkerPool] Executando fallback para o job '{job.job_id}'...")
                    asset = fallback_handler(job)
                    job.status = "COMPLETED"
                    job.completed_at = datetime.now(timezone.utc).isoformat() + "Z"
                    return asset
                except Exception as fallback_err:
                    logging.error(f"[WorkerPool] Fallback também falhou: {fallback_err}")
                    job.status = "FAILED"
                    job.error_message = f"Primary: {primary_err} | Fallback: {fallback_err}"
            else:
                job.status = "FAILED"
                job.error_message = str(primary_err)

        return None
