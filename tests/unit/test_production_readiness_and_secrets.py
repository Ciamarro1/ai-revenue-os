import pytest
from src.revenue_os.analytics.economic_brain import EconomicBrain
from src.revenue_os.observability.production_readiness import ProductionReadinessEngine
from src.revenue_os.security.secrets_manager import SecretsManager
from src.revenue_os.factory.offer_factory import OfferFactory
from src.revenue_os.analytics.opportunity_schemas import RevenueOpportunity

def test_economic_brain_reusability_gain():
    brain = EconomicBrain()
    res_single = brain.calculate_utility(
        expected_revenue=10.0, infra_cost=2.0, risk_factor=0.05, reusability_channels_count=1
    )
    res_multi = brain.calculate_utility(
        expected_revenue=10.0, infra_cost=2.0, risk_factor=0.05, reusability_channels_count=4
    )

    assert res_multi["reusability_gain_value"] > res_single["reusability_gain_value"]
    assert res_multi["total_utility_score"] > res_single["total_utility_score"]

def test_production_readiness_engine(tmp_path):
    engine = ProductionReadinessEngine(base_dir=tmp_path, max_daily_budget_usd=50.0)

    # 1. Health check normal
    health = engine.run_production_health_check(current_daily_spend_usd=20.0)
    assert health["production_status"] == "READY"
    assert health["circuit_breaker_active"] is False

    # 2. Excesso de orçamento
    over_health = engine.run_production_health_check(current_daily_spend_usd=60.0)
    assert over_health["production_status"] == "BUDGET_CAP_EXCEEDED"

    # 3. Recuperação de experimentos
    recovered = engine.recover_interrupted_experiments([
        {"id": "EXP-101", "status": "INTERRUPTED", "last_state": "Imagem/Vídeo"}
    ])
    assert len(recovered) == 1
    assert recovered[0]["action"] == "RESUME_AT_LAST_STATE"

def test_secrets_manager():
    sm = SecretsManager(environment="development")
    masked = sm.mask_secret("sk-proj-123456789abc")

    assert "..." in masked
    assert masked.startswith("sk-p")
    audit = sm.audit_security_governance()
    assert audit["environment"] == "development"

def test_lean_offer_factory():
    factory = OfferFactory()
    opp = RevenueOpportunity(
        id="OPP-999",
        marketplace="Hotmart",
        product_name="Productivity Blueprint",
        category="productivity",
        commission_rate=0.60,
        avg_commission_usd=50.0
    )

    manifest = factory.create_offer_manifest(opp)
    assert manifest.product_name == "Productivity Blueprint"
    assert "Productivity Blueprint" in manifest.title
    props = manifest.to_astro_props()
    assert props["title"] == manifest.title
