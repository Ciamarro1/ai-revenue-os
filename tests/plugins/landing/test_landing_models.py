from src.revenue_os.plugins.landing.models import (
    BuildResult,
    DeploymentRecord,
    RollbackRecord,
    LandingDeploymentConfig
)

def test_build_result_schema():
    b = BuildResult(
        build_id="B-1",
        framework="astro",
        manifest_id="OFFER-1",
        build_fingerprint="abc123sha256"
    )
    assert b.build_id == "B-1"
    assert b.framework == "astro"
    assert b.build_fingerprint == "abc123sha256"

def test_deployment_record_schema():
    d = DeploymentRecord(
        deployment_id="DEP-1",
        version="v1.0.0",
        framework="nextjs",
        cdn_provider="vercel",
        public_url="https://app.vercel.app",
        build_fingerprint="abc123sha256"
    )
    assert d.deployment_id == "DEP-1"
    assert d.cdn_provider == "vercel"
    assert d.is_active is True

def test_rollback_record_schema():
    r = RollbackRecord(
        rollback_id="RB-1",
        previous_deployment_id="DEP-2",
        restored_deployment_id="DEP-1",
        restored_version="v1.0.0"
    )
    assert r.restored_deployment_id == "DEP-1"
    assert r.status == "SUCCESS"
