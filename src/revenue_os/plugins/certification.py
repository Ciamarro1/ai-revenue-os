from typing import Dict, Any, Optional
from src.revenue_os.plugins.base_plugin import BasePlugin
from src.reality.oss_catalog.governance import OSSEvaluationScorecard
from src.reality.oss_catalog.catalog import OSSEntry

class PluginCertificationEngine:
    """
    Plugin Certification Engine (Fase III Live Operations).
    Avalia a saúde, latência, uso de memória e segurança de plugins no Plugin Runtime,
    certificando-os como EXPERIMENTAL, STABLE, PRODUCTION ou DEPRECATED.
    """

    def certify_plugin(
        self,
        plugin: BasePlugin,
        startup_latency_sec: float = 0.45,
        memory_usage_mb: float = 48.0,
        oss_entry: Optional[OSSEntry] = None
    ) -> Dict[str, Any]:
        health = plugin.health_check()
        is_healthy = health.get("status") == "HEALTHY"
        low_latency = startup_latency_sec <= 2.0
        low_memory = memory_usage_mb <= 256.0

        governance_passed = True
        if oss_entry:
            scorecard = OSSEvaluationScorecard()
            gov_res = scorecard.evaluate_entry(oss_entry)
            governance_passed = gov_res.overall_score >= 70.0

        criteria = {
            "health_check_pass": is_healthy,
            "startup_latency_pass": low_latency,
            "memory_usage_pass": low_memory,
            "governance_pass": governance_passed
        }

        passed_count = sum(1 for v in criteria.values() if v)

        if passed_count == 4:
            status = "PRODUCTION"
        elif passed_count == 3:
            status = "STABLE"
        elif passed_count >= 2:
            status = "EXPERIMENTAL"
        else:
            status = "DEPRECATED"

        return {
            "plugin_name": plugin.plugin_name,
            "category": plugin.category,
            "certification_status": status,
            "passed_criteria": criteria,
            "is_authorized_for_production": status in ["PRODUCTION", "STABLE"]
        }
