from dataclasses import dataclass, field
from typing import Dict, Any, List
import sqlite3
from src.revenue_os.analytics.database import ExperimentDatabase

@dataclass
class DashboardSnapshot:
    research_queue_size: int
    rendering_queue_size: int
    calibration_queue_size: int
    pending_metrics_size: int
    factory_health: Dict[str, Any]
    policy_violations: int
    pinterest_state: Dict[str, Any]
    queue_stats: Dict[str, Any] = field(default_factory=dict)
    board_stats: List[Dict[str, Any]] = field(default_factory=list)

class MetricsAggregator:
    def __init__(self, db: ExperimentDatabase):
        self.db = db
        
    def get_snapshot(self) -> DashboardSnapshot:
        with self.db._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute("SELECT COUNT(*) as count FROM experiments WHERE status IN ('PUBLISHED', 'CALIBRATING')")
            calib_queue = c.fetchone()['count']
            
            c.execute("SELECT COUNT(*) as count FROM experiment_events WHERE event_type LIKE '%POLICY_BLOCK%'")
            violations = c.fetchone()['count']
            
            c.execute("SELECT COUNT(*) as count FROM experiments WHERE status = 'HYPOTHESIS_FORMED'")
            render_queue = c.fetchone()['count']
            
            c.execute("SELECT COUNT(*) as count FROM experiments WHERE status = 'CREATED'")
            research_queue = c.fetchone()['count']
            
            c.execute("SELECT * FROM factory_health ORDER BY timestamp DESC LIMIT 10")
            fh_rows = c.fetchall()
            
            if fh_rows:
                avg_time = sum(r['render_time'] for r in fh_rows) / len(fh_rows)
                avg_cpu = sum(r['avg_cpu'] for r in fh_rows) / len(fh_rows)
                avg_ram = sum(r['avg_ram'] for r in fh_rows) / len(fh_rows)
            else:
                avg_time = avg_cpu = avg_ram = 0.0
                
            fh = {
                "avg_render_time": round(avg_time, 2),
                "avg_cpu": round(avg_cpu, 2),
                "avg_ram": round(avg_ram, 2),
                "status": "Healthy" if avg_time < 300 else "Degraded"
            }
            
            # Get Pinterest State from database (with Trust Score)
            pinterest_state = None
            try:
                c.execute("SELECT value_json FROM system_state WHERE key = 'PINTEREST_ACC_STATE'")
                row = c.fetchone()
                if row:
                    import json
                    pinterest_state = json.loads(row[0])
            except Exception:
                pass
                
            if not pinterest_state:
                pinterest_state = {
                    "trust_score": 100,
                    "state": "HEALTHY",
                    "consecutive_failures": 0,
                    "cooldown_until": None,
                    "last_post_time": None,
                    "next_scheduled_post": None,
                    "account_age_days": 0,
                    "total_posts": 0,
                    "total_successes": 0,
                    "score_history": [],
                }
                
            # Compute dynamic posts today
            from datetime import datetime, timezone
            today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            posts_today = 0
            try:
                c.execute(
                    "SELECT COUNT(*) FROM experiments WHERE status IN ('PUBLISHED', 'COMPLETED') AND published_at LIKE ?",
                    (f"{today_prefix}%",)
                )
                p_row = c.fetchone()
                if p_row:
                    posts_today = p_row[0] or 0
            except Exception:
                pass
            pinterest_state["posts_today"] = posts_today
            
            # Dynamic daily limit
            daily_limit = 5
            try:
                from src.reality.social.pinterest.safety_coordinator import PinterestSafetyCoordinator
                coord = PinterestSafetyCoordinator(self.db)
                daily_limit = coord.get_daily_limit()
            except Exception:
                pass
            pinterest_state["daily_limit"] = daily_limit
            
            # Queue stats
            queue_stats = {}
            try:
                c.execute("SELECT COUNT(*) FROM publication_queue WHERE status = 'pending'")
                queue_stats["pending"] = c.fetchone()[0] or 0
                c.execute("SELECT COUNT(*) FROM publication_queue WHERE status = 'processing'")
                queue_stats["processing"] = c.fetchone()[0] or 0
                c.execute("SELECT COUNT(*) FROM publication_queue WHERE status = 'published' AND processed_at LIKE ?",
                          (f"{today_prefix}%",))
                queue_stats["published_today"] = c.fetchone()[0] or 0
            except Exception:
                pass
            
            # Board stats
            board_stats = []
            try:
                c.execute("SELECT * FROM board_metrics ORDER BY total_posts DESC")
                for row in c.fetchall():
                    board_stats.append(dict(row))
            except Exception:
                pass

            return DashboardSnapshot(
                research_queue_size=research_queue,
                rendering_queue_size=render_queue,
                calibration_queue_size=calib_queue,
                pending_metrics_size=calib_queue,
                factory_health=fh,
                policy_violations=violations,
                pinterest_state=pinterest_state,
                queue_stats=queue_stats,
                board_stats=board_stats,
            )
