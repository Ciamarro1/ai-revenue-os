import pytest
from src.revenue_os.observability.platform_maturity import PlatformMaturityEngine

def test_platform_maturity_index_calculation():
    engine = PlatformMaturityEngine()
    
    # Estado inicial de produção v5.0 (sem receita confirmada ainda)
    res_v5 = engine.calculate_pmi(confirmed_revenue_ready=False)
    assert res_v5["pmi_score"] == 80
    assert res_v5["maturity_level"] == "LIVE_OPERATIONAL"

    # Estado final com receita confirmada PM-3/PM-4
    res_full = engine.calculate_pmi(confirmed_revenue_ready=True)
    assert res_full["pmi_score"] == 100
    assert res_full["maturity_level"] == "PRODUCTION_SCALABLE"

def test_kernel_lock_files_exist():
    from pathlib import Path
    lock_doc = Path("docs/architecture/kernel_lock.md")
    assert lock_doc.exists()
