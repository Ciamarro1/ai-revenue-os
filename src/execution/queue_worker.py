import uuid
import logging
import sqlite3
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from src.revenue_os.analytics.database import ExperimentDatabase

logger = logging.getLogger("revenue_os.queue_worker")


class QueueWorker:
    """
    Consome jobs da tabela publication_queue e gerencia estados persistentes.
    Desacopla o ato de 'decidir publicar' do ato de 'executar a publicação'.
    Se o sistema cair, os jobs são retomados automaticamente.
    """

    def __init__(self, db: ExperimentDatabase, safety_coordinator=None):
        self.db = db
        self.coordinator = safety_coordinator

    def enqueue(self, experiment_id: str, media_path: str, title: str,
                description: str, link: str, board: str = "AI Revenue OS",
                scheduled_at: Optional[str] = None) -> str:
        """
        Insere um novo job na fila de publicação.
        Retorna o job_id gerado.
        """
        job_id = f"JOB-{uuid.uuid4().hex[:8].upper()}"
        
        if not scheduled_at:
            scheduled_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO publication_queue 
                    (job_id, experiment_id, platform, media_path, title, description, link, board, 
                     status, attempts, max_attempts, scheduled_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (job_id, experiment_id, "pinterest", media_path, title, description, link, board,
                      "pending", 0, 3, scheduled_at))
                conn.commit()
            logger.info(f"Job enfileirado: {job_id} para {experiment_id} (agendado: {scheduled_at})")
        except Exception as e:
            logger.error(f"Erro ao enfileirar job: {e}")
            raise
        
        return job_id

    def get_next_job(self) -> Optional[Dict[str, Any]]:
        """
        Busca o próximo job pendente com scheduled_at <= agora.
        Retorna None se não houver jobs prontos.
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        try:
            with self.db._get_conn() as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute('''
                    SELECT * FROM publication_queue 
                    WHERE status = 'pending' AND scheduled_at <= ?
                    ORDER BY scheduled_at ASC LIMIT 1
                ''', (now,))
                row = c.fetchone()
                if row:
                    return dict(row)
        except Exception as e:
            logger.error(f"Erro ao buscar proximo job: {e}")
        
        return None

    def process_next(self) -> Optional[Dict[str, Any]]:
        """
        Gets the next pending job where scheduled_at <= now.
        Checks safety coordinator before processing.
        If healthy, marks the job as 'processing' and returns it.
        """
        from src.reality.social.pinterest.safety_coordinator import PinterestSafetyCoordinator
        coord = self.coordinator or PinterestSafetyCoordinator(self.db)
        
        state_data = coord.get_state()
        if state_data.get("state") == "COOLDOWN":
            logger.info("Pinterest safety coordinator is in COOLDOWN. Skipping processing.")
            return None
            
        job = self.get_next_job()
        if job:
            self.mark_processing(job["job_id"])
            return job
        return None

    def update_job_status(self, job_id: str, status: str, error_message: Optional[str] = None,
                          increment_attempts: bool = False):
        """Atualiza o status de um job na fila."""
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                
                if increment_attempts:
                    c.execute('''
                        UPDATE publication_queue 
                        SET status = ?, error_message = ?, processed_at = ?, attempts = attempts + 1
                        WHERE job_id = ?
                    ''', (status, error_message, now, job_id))
                else:
                    c.execute('''
                        UPDATE publication_queue 
                        SET status = ?, error_message = ?, processed_at = ?
                        WHERE job_id = ?
                    ''', (status, error_message, now, job_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao atualizar job {job_id}: {e}")

    def mark_processing(self, job_id: str):
        """Marca um job como 'processing' (em andamento)."""
        self.update_job_status(job_id, "processing")

    def mark_published(self, job_id: str):
        """Marca um job como 'published' (sucesso)."""
        self.update_job_status(job_id, "published")
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('SELECT experiment_id FROM publication_queue WHERE job_id = ?', (job_id,))
                row = c.fetchone()
                if row:
                    exp_id = row[0]
                    c.execute("UPDATE experiments SET status = 'OBSERVING' WHERE experiment_id = ?", (exp_id,))
                    conn.commit()
                    logger.info(f"Experiment {exp_id} transitioned to OBSERVING state after successful publication.")
        except Exception as e:
            logger.error(f"Error transitioning experiment to OBSERVING status: {e}")

    def mark_failed(self, job_id: str, error_message: str):
        """Marca um job como 'failed' e incrementa tentativas."""
        self.update_job_status(job_id, "failed", error_message=error_message, increment_attempts=True)
        try:
            with self.db._get_conn() as conn:
                conn.row_factory = sqlite3.Row if hasattr(sqlite3, 'Row') else None
                c = conn.cursor()
                c.execute('SELECT experiment_id, attempts, max_attempts FROM publication_queue WHERE job_id = ?', (job_id,))
                row = c.fetchone()
                if row:
                    exp_id = row[0] if isinstance(row, tuple) else row["experiment_id"]
                    attempts = row[1] if isinstance(row, tuple) else row["attempts"]
                    max_attempts = row[2] if isinstance(row, tuple) else row["max_attempts"]
                    if attempts >= max_attempts:
                        c.execute("UPDATE experiments SET status = 'FAILED_PERMANENT' WHERE experiment_id = ?", (exp_id,))
                        conn.commit()
                        logger.warning(f"Experiment {exp_id} transitioned to FAILED_PERMANENT after job failure limits reached.")
        except Exception as e:
            logger.error(f"Error checking and updating experiment state upon job failure: {e}")

    def recover_stale_jobs(self):
        """
        Recupera jobs travados em 'processing' (crash mid-publish).
        Reseta para 'pending' se attempts < max_attempts.
        """
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    UPDATE publication_queue 
                    SET status = 'pending' 
                    WHERE status = 'processing' AND attempts < max_attempts
                ''')
                recovered = c.rowcount
                
                c.execute('''
                    UPDATE publication_queue 
                    SET status = 'failed', error_message = 'MAX_ATTEMPTS_EXCEEDED_ON_RECOVERY'
                    WHERE status = 'processing' AND attempts >= max_attempts
                ''')
                failed = c.rowcount
                conn.commit()
                
                if recovered > 0 or failed > 0:
                    logger.info(f"Recovery: {recovered} jobs restaurados, {failed} marcados como falha permanente")
        except Exception as e:
            logger.error(f"Erro na recuperacao de jobs: {e}")

    def get_queue_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da fila de publicação."""
        stats = {
            "pending": 0, "processing": 0,
            "published_today": 0, "failed_today": 0, "total": 0
        }
        try:
            today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            with self.db._get_conn() as conn:
                c = conn.cursor()
                
                c.execute("SELECT COUNT(*) FROM publication_queue WHERE status = 'pending'")
                stats["pending"] = c.fetchone()[0] or 0
                
                c.execute("SELECT COUNT(*) FROM publication_queue WHERE status = 'processing'")
                stats["processing"] = c.fetchone()[0] or 0
                
                c.execute("SELECT COUNT(*) FROM publication_queue WHERE status = 'published' AND processed_at LIKE ?",
                          (f"{today_prefix}%",))
                stats["published_today"] = c.fetchone()[0] or 0
                
                c.execute("SELECT COUNT(*) FROM publication_queue WHERE status = 'failed' AND processed_at LIKE ?",
                          (f"{today_prefix}%",))
                stats["failed_today"] = c.fetchone()[0] or 0
                
                c.execute("SELECT COUNT(*) FROM publication_queue")
                stats["total"] = c.fetchone()[0] or 0
                
        except Exception as e:
            logger.error(f"Erro ao calcular estatisticas da fila: {e}")
        
        return stats
