import pytest
from datetime import datetime, timezone, timedelta

from src.revenue_os.analytics.database import ExperimentDatabase
from src.reality.social.pinterest.safety_coordinator import (
    PinterestSafetyCoordinator, TRUST_SCORE_EVENTS, RAMPUP_POLICY, BACKOFF_DELAYS
)


@pytest.fixture
def temp_db():
    db = ExperimentDatabase(":memory:")
    return db


@pytest.fixture
def coordinator(temp_db):
    return PinterestSafetyCoordinator(db=temp_db)


# ─── Trust Score ───

def test_initial_trust_score(coordinator):
    state = coordinator.get_state()
    assert state["trust_score"] == 100
    assert state["state"] == "HEALTHY"


def test_trust_score_publish_success(coordinator):
    new_score = coordinator.update_trust_score("PUBLISH_SUCCESS")
    assert new_score == 100  # Capped at 100


def test_trust_score_captcha(coordinator):
    new_score = coordinator.update_trust_score("CAPTCHA_DETECTED")
    assert new_score == 80  # 100 - 20


def test_trust_score_rate_limit(coordinator):
    new_score = coordinator.update_trust_score("RATE_LIMIT_429")
    assert new_score == 50  # 100 - 50


def test_trust_score_login_required(coordinator):
    new_score = coordinator.update_trust_score("LOGIN_REQUIRED")
    assert new_score == 70  # 100 - 30


def test_trust_score_derive_healthy(coordinator):
    assert coordinator._derive_state(100) == "HEALTHY"
    assert coordinator._derive_state(80) == "HEALTHY"


def test_trust_score_derive_warning(coordinator):
    assert coordinator._derive_state(79) == "WARNING"
    assert coordinator._derive_state(50) == "WARNING"


def test_trust_score_derive_cooldown(coordinator):
    assert coordinator._derive_state(49) == "COOLDOWN"
    assert coordinator._derive_state(0) == "COOLDOWN"


def test_trust_score_floor_zero(coordinator):
    coordinator.update_trust_score("ACCOUNT_SUSPENDED")
    state = coordinator.get_state()
    assert state["trust_score"] == 0
    assert state["state"] == "COOLDOWN"


def test_score_history(coordinator):
    coordinator.update_trust_score("CAPTCHA_DETECTED")
    coordinator.update_trust_score("PUBLISH_SUCCESS")
    state = coordinator.get_state()
    history = state.get("score_history", [])
    assert len(history) == 2
    assert history[0]["event"] == "CAPTCHA_DETECTED"
    assert history[1]["event"] == "PUBLISH_SUCCESS"


# ─── Ramp-up ───

def test_rampup_initial_limit(coordinator):
    limit = coordinator.get_daily_limit()
    assert limit == 5  # Dia 0, Trust 100


def test_rampup_after_7_days(coordinator, temp_db):
    state = coordinator.get_state()
    state["first_post_date"] = (datetime.now(timezone.utc) - timedelta(days=8)).strftime("%Y-%m-%dT%H:%M:%SZ")
    state["account_age_days"] = 8
    temp_db.set_system_state("PINTEREST_ACC_STATE", state)
    
    limit = coordinator.get_daily_limit()
    assert limit == 8


def test_rampup_regression_on_low_trust(coordinator, temp_db):
    state = coordinator.get_state()
    state["first_post_date"] = (datetime.now(timezone.utc) - timedelta(days=15)).strftime("%Y-%m-%dT%H:%M:%SZ")
    state["account_age_days"] = 15
    state["trust_score"] = 75  # Abaixo do min_trust (85) da fase 14-21 dias
    temp_db.set_system_state("PINTEREST_ACC_STATE", state)
    
    limit = coordinator.get_daily_limit()
    # Deve regredir para uma fase com min_trust <= 75
    assert limit <= 5


# ─── Backoff Exponencial ───

def test_backoff_first_attempt(coordinator):
    delay = coordinator.get_retry_delay(0)
    assert 180 <= delay <= 225  # 3min + jitter (0 a 45s)


def test_backoff_second_attempt(coordinator):
    delay = coordinator.get_retry_delay(1)
    assert 1500 <= delay <= 1875  # 25min + jitter


def test_backoff_third_attempt(coordinator):
    delay = coordinator.get_retry_delay(2)
    assert 7200 <= delay <= 9000  # 2h + jitter


def test_backoff_exhausted(coordinator):
    delay = coordinator.get_retry_delay(3)
    assert delay == -1  # Deve entrar em cooldown


# ─── Handle Publish Result ───

def test_handle_success_updates_trust(coordinator):
    coordinator.handle_publish_result(success=True)
    state = coordinator.get_state()
    assert state["trust_score"] == 100  # +2 capped at 100
    assert state["total_posts"] == 1
    assert state["total_successes"] == 1
    assert state["first_post_date"] is not None


def test_handle_success_slow_publish(coordinator):
    coordinator.handle_publish_result(success=True, publish_duration_sec=35.0)
    state = coordinator.get_state()
    assert state["trust_score"] == 95  # -5 for slow publish


def test_handle_failure_critical(coordinator):
    coordinator.handle_publish_result(success=False, error_type="CAPTCHA_DETECTED")
    state = coordinator.get_state()
    assert state["state"] == "COOLDOWN"
    assert state["cooldown_until"] is not None


def test_handle_failure_non_critical(coordinator):
    coordinator.handle_publish_result(success=False, error_type="PUBLISH_SLOW")
    state = coordinator.get_state()
    assert state["trust_score"] < 100
    assert state["consecutive_failures"] == 1


# ─── Cooldown Expiration ───

def test_cooldown_expiration(coordinator, temp_db):
    past_time = (datetime.now(timezone.utc) - timedelta(hours=25)).strftime("%Y-%m-%dT%H:%M:%SZ")
    state = coordinator.get_state()
    state["state"] = "COOLDOWN"
    state["trust_score"] = 45  # After +10 recovery → 55 (WARNING, not COOLDOWN)
    state["consecutive_failures"] = 3
    state["cooldown_until"] = past_time
    temp_db.set_system_state("PINTEREST_ACC_STATE", state)
    
    current_state = coordinator.get_state()
    assert current_state["state"] != "COOLDOWN"  # Auto-recovered
    assert current_state["trust_score"] == 55  # 45 + 10 recovery
    assert current_state["consecutive_failures"] == 0
