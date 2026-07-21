from typing import Dict, Any, Optional
from src.revenue_os.plugins.base_plugin import BasePlugin
from src.revenue_os.plugins.landing.deployment_engine import LandingDeploymentEngine

class NextjsLandingPlugin(BasePlugin):
    """
    NextjsLandingPlugin (Sprint O4).
    Plugin de Geração e Deploy de Landing Pages utilizando Next.js App Router / SSG.
    """

    def __init__(self, deployment_engine: Optional[LandingDeploymentEngine] = None):
        self.engine = deployment_engine or LandingDeploymentEngine()
        self._initialized = False

    @property
    def plugin_name(self) -> str:
        return "nextjs"

    @property
    def category(self) -> str:
        return "landing"

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self._initialized else "UNHEALTHY",
            "engine": "Next.js 15 App Router",
            "framework": "nextjs",
            "registered_cdns": list(self.engine._cdn_providers.keys())
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "build_and_deploy")
        cdn = payload.get("cdn_provider", "vercel")

        if action == "build":
            build_res = self.engine.build_landing(payload, framework="nextjs")
            return {"status": "SUCCESS", "action": action, "build_result": build_res.model_dump()}

        elif action == "deploy":
            build_res = self.engine.build_landing(payload, framework="nextjs")
            dep_rec = self.engine.deploy_landing(build_res, cdn_name=cdn)
            return {"status": "SUCCESS", "action": action, "deployment": dep_rec.model_dump()}

        elif action == "build_and_deploy":
            build_res = self.engine.build_landing(payload, framework="nextjs")
            dep_rec = self.engine.deploy_landing(build_res, cdn_name=cdn)
            return {
                "status": "SUCCESS",
                "action": action,
                "landing_url": dep_rec.public_url,
                "version": dep_rec.version,
                "build_fingerprint": dep_rec.build_fingerprint,
                "built_with": "Next.js 15 App Router + React Server Components",
                "deployment": dep_rec.model_dump()
            }

        elif action == "rollback":
            dep_id = payload.get("deployment_id", "")
            rb_rec = self.engine.rollback(dep_id)
            return {"status": "SUCCESS", "action": action, "rollback": rb_rec.model_dump()}

        raise ValueError(f"Ação desconhecida '{action}' para NextjsLandingPlugin")

    def shutdown(self) -> None:
        self._initialized = False
