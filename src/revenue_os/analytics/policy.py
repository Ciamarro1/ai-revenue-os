import time
import logging
from typing import Dict, Any
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.schemas import ExperimentPolicy

logger = logging.getLogger("revenue_os.policy")

class PolicyEngine:
    """
    Motor que enforça os limites de segurança (ExperimentPolicy).
    Evita publicações excessivas e controla custos de geração.
    Integra com ramp-up automático via PinterestSafetyCoordinator.
    """
    def __init__(self, db: ExperimentDatabase, policy: ExperimentPolicy):
        self.db = db
        self.policy = policy
        
    def _get_dynamic_daily_limit(self) -> int:
        """
        Consulta o PinterestSafetyCoordinator para obter o limite dinâmico.
        Fallback: usa self.policy.max_daily_posts se o coordenador não estiver disponível.
        """
        try:
            from src.revenue_os.analytics.feature_flags import FeatureFlags
            flags = FeatureFlags(db=self.db)
            if flags.is_enabled("ENABLE_AUTO_RAMPUP"):
                from src.reality.social.pinterest.safety_coordinator import PinterestSafetyCoordinator
                coordinator = PinterestSafetyCoordinator(self.db)
                return coordinator.get_daily_limit()
        except Exception as e:
            logger.warning(f"Fallback para limite estático: {e}")
        
        return self.policy.max_daily_posts
        
    def check_can_publish(self, quality_score: float, confidence: float, estimated_cost: float) -> Dict[str, Any]:
        """Avalia as políticas antes de enviar pro Publisher."""
        from datetime import datetime, timezone
        import sqlite3
        
        today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        current_daily_posts = 0
        current_daily_cost = 0.0
        
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT COUNT(*), SUM(generation_cost_usd) FROM experiments WHERE status IN ('PUBLISHED', 'COMPLETED') AND published_at LIKE ?",
                    (f"{today_prefix}%",)
                )
                row = c.fetchone()
                if row:
                    current_daily_posts = row[0] or 0
                    current_daily_cost = row[1] or 0.0
        except sqlite3.OperationalError as e:
            logger.warning(f"Erro ao consultar limites diarios no DB: {e}")
        
        # Usa limite dinâmico (ramp-up) em vez de fixo
        daily_limit = self._get_dynamic_daily_limit()
        
        if current_daily_posts >= daily_limit:
            return {"allowed": False, "reason": "max_daily_posts_exceeded", "limit": daily_limit, "current": current_daily_posts}
            
        if current_daily_cost + estimated_cost > self.policy.max_daily_generation_cost:
            return {"allowed": False, "reason": "max_daily_generation_cost_exceeded"}
            
        if self.policy.require_quality_gate and quality_score < 0.8:
            return {"allowed": False, "reason": "quality_score_too_low"}
            
        if confidence < self.policy.min_confidence_to_publish:
            return {"allowed": False, "reason": "confidence_too_low"}
            
        return {"allowed": True, "reason": "ok", "daily_limit": daily_limit, "posts_today": current_daily_posts}
