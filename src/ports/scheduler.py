from abc import ABC, abstractmethod
from typing import Callable, Any, Dict, Optional

class SchedulerPort(ABC):
    """
    Scheduler Port interface.
    Decouples task scheduling and recurring runners (APScheduler, Temporal Schedules, Cron).
    """
    @abstractmethod
    def schedule_job(
        self,
        job_id: str,
        func: Callable[..., Any],
        cron_expression: str,
        args: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Agenda uma tarefa recorrente baseada em expressão Cron."""
        pass

    @abstractmethod
    def cancel_job(self, job_id: str):
        """Cancela uma tarefa agendada pelo identificador único."""
        pass
