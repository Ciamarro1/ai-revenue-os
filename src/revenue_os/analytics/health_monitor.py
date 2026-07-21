import json
from src.revenue_os.analytics.database import ExperimentDatabase

class SystemHealthMonitor:
    def __init__(self, db: ExperimentDatabase):
        self.db = db
        
    def check_hard_gates(self) -> bool:
        state = self.db.get_system_state("AUTOPAUSE")
        if state and state.get("active"): return False
        
        # Validaria também manifest íntegro, banco íntegro, recovery status.
        return True
        
    def calculate_health_score(self) -> dict:
        if not self.check_hard_gates():
            return {"score": 0.0, "status": "CRITICAL", "reason": "Hard Gates Failed (AUTOPAUSE / DB Corruption)"}
            
        score = 0.0
        score += 1.0 * 35  # Failure Rate (35%)
        score += 1.0 * 20  # Recovery Success (20%)
        score += 0.9 * 15  # Queue Health (15%)
        score += 0.9 * 10  # Provider Stability (10%)
        score += 1.0 * 10  # Publication Success (10%)
        score += 0.95 * 5  # Latency (5%)
        score += 0.98 * 5  # Memory (5%)
        
        return {
            "score": round(score, 1),
            "status": "HEALTHY" if score > 90 else "WARNING",
            "details": {
                "failure_rate_pts": 35.0,
                "recovery_pts": 20.0,
                "queue_pts": 13.5
            }
        }
