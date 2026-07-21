import heapq
from typing import Dict, List, Optional
from src.revenue_os.plugins.creatives.models import CreativeJob

class CreativeJobQueue:
    """
    Fila de Jobs com Prioridades (HIGH=3, MEDIUM=2, LOW=1).
    """

    PRIORITY_MAP = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}

    def __init__(self):
        self._heap = []
        self._jobs: Dict[str, CreativeJob] = {}
        self._counter = 0  # Garante ordenação estável em empates

    def enqueue(self, job: CreativeJob) -> None:
        prio = self.PRIORITY_MAP.get(job.priority.upper(), 2)
        self._counter += 1
        heapq.heappush(self._heap, (prio, self._counter, job.job_id))
        self._jobs[job.job_id] = job

    def dequeue(self) -> Optional[CreativeJob]:
        while self._heap:
            _, _, job_id = heapq.heappop(self._heap)
            job = self._jobs.get(job_id)
            if job and job.status == "QUEUED":
                job.status = "PROCESSING"
                return job
        return None

    def get_job(self, job_id: str) -> Optional[CreativeJob]:
        return self._jobs.get(job_id)

    def list_all(self) -> List[CreativeJob]:
        return list(self._jobs.values())

    def pending_count(self) -> int:
        return sum(1 for j in self._jobs.values() if j.status == "QUEUED")
