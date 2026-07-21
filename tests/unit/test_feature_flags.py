import pytest
import json
import time
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.feature_flags import FeatureFlags


@pytest.fixture
def temp_db():
    db = ExperimentDatabase(":memory:")
    return db


@pytest.fixture
def temp_json(tmp_path):
    config = {
        "ENABLE_PLAYWRIGHT": True,
        "ENABLE_BROWSER_USE": False,
        "ENABLE_SMART_SCHEDULING": True,
    }
    p = tmp_path / "feature_flags.json"
    p.write_text(json.dumps(config))
    return str(p)


def test_defaults(temp_db):
    """Defaults são retornados quando não há JSON nem DB override."""
    flags = FeatureFlags(db=temp_db, config_path="/nonexistent/path.json")
    assert flags.is_enabled("ENABLE_PLAYWRIGHT") is True
    assert flags.is_enabled("ENABLE_SMART_SCHEDULING") is False
    assert flags.is_enabled("ENABLE_TRUST_SCORE") is True


def test_json_override(temp_db, temp_json):
    """JSON override sobrescreve defaults."""
    flags = FeatureFlags(db=temp_db, config_path=temp_json)
    assert flags.is_enabled("ENABLE_BROWSER_USE") is False
    assert flags.is_enabled("ENABLE_SMART_SCHEDULING") is True


def test_db_override(temp_db, temp_json):
    """DB override tem prioridade sobre JSON."""
    # JSON diz BROWSER_USE = False
    # DB vai dizer BROWSER_USE = True
    temp_db.set_system_state("FEATURE_FLAGS", {"ENABLE_BROWSER_USE": True})
    flags = FeatureFlags(db=temp_db, config_path=temp_json)
    assert flags.is_enabled("ENABLE_BROWSER_USE") is True


def test_is_enabled_unknown(temp_db):
    """Flags desconhecidas retornam False."""
    flags = FeatureFlags(db=temp_db, config_path="/nonexistent/path.json")
    assert flags.is_enabled("ENABLE_UNKNOWN_FEATURE") is False


def test_set_override(temp_db):
    """set_override persiste no DB."""
    flags = FeatureFlags(db=temp_db, config_path="/nonexistent/path.json")
    assert flags.is_enabled("ENABLE_SMART_SCHEDULING") is False
    flags.set_override("ENABLE_SMART_SCHEDULING", True)
    assert flags.is_enabled("ENABLE_SMART_SCHEDULING") is True
    
    # Recarrega do DB
    flags2 = FeatureFlags(db=temp_db, config_path="/nonexistent/path.json")
    assert flags2.is_enabled("ENABLE_SMART_SCHEDULING") is True


def test_get_all(temp_db):
    """get_all retorna todas as flags."""
    flags = FeatureFlags(db=temp_db, config_path="/nonexistent/path.json")
    all_flags = flags.get_all()
    assert isinstance(all_flags, dict)
    assert "ENABLE_PLAYWRIGHT" in all_flags
    assert "ENABLE_TRUST_SCORE" in all_flags
    assert len(all_flags) >= 10


def test_cache_expiry(temp_db):
    """Cache expira após TTL."""
    flags = FeatureFlags(db=temp_db, config_path="/nonexistent/path.json")
    assert flags.is_enabled("ENABLE_SMART_SCHEDULING") is False
    
    # Override no DB diretamente
    temp_db.set_system_state("FEATURE_FLAGS", {"ENABLE_SMART_SCHEDULING": True})
    
    # Cache ainda ativo - não vê a mudança
    assert flags.is_enabled("ENABLE_SMART_SCHEDULING") is False
    
    # Força expiração do cache
    flags._cache_time = 0
    assert flags.is_enabled("ENABLE_SMART_SCHEDULING") is True
