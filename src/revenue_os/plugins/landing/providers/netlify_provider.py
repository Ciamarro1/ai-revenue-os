import hashlib
from src.revenue_os.plugins.landing.providers.base_cdn_provider import BaseCDNProvider
from src.revenue_os.plugins.landing.models import BuildResult, DeploymentRecord, RollbackRecord

class NetlifyProvider(BaseCDNProvider):
    """
    Adaptador de Deploy para Netlify.
    """

    @property
    def cdn_name(self) -> str:
        return "netlify"

    def deploy_build(self, build_result: BuildResult, version: str) -> DeploymentRecord:
        dep_id = f"NETLIFY-DEP-{build_result.build_fingerprint[:8]}-{version.split('-')[-1]}"
        project_slug = build_result.manifest_id.lower().replace("_", "-").replace("offer-", "").replace("manifest-", "")
        url = f"https://{project_slug}.netlify.app"

        return DeploymentRecord(
            deployment_id=dep_id,
            version=version,
            framework=build_result.framework,
            cdn_provider=self.cdn_name,
            public_url=url,
            status="ACTIVE",
            build_fingerprint=build_result.build_fingerprint,
            is_active=True,
            classification_status="LOCAL_TEST"
        )

    def rollback_deployment(self, current_deployment: DeploymentRecord, target_deployment: DeploymentRecord) -> RollbackRecord:
        rollback_id = f"NETLIFY-RB-{hashlib.md5(current_deployment.deployment_id.encode()).hexdigest()[:8]}"
        current_deployment.is_active = False
        current_deployment.status = "ROLLED_BACK"
        target_deployment.is_active = True
        target_deployment.status = "ACTIVE"

        return RollbackRecord(
            rollback_id=rollback_id,
            previous_deployment_id=current_deployment.deployment_id,
            restored_deployment_id=target_deployment.deployment_id,
            restored_version=target_deployment.version,
            status="SUCCESS"
        )
