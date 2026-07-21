import pytest
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

from src.revenue_os.analytics.database import ExperimentDatabase
from src.reality.social.pinterest.safety_coordinator import PinterestSafetyCoordinator


@pytest.fixture
def temp_db():
    db = ExperimentDatabase(":memory:")
    return db


@pytest.fixture
def coordinator(temp_db):
    return PinterestSafetyCoordinator(db=temp_db)


def test_init_state(coordinator):
    state = coordinator.get_state()
    assert state["trust_score"] == 100
    assert state["state"] == "HEALTHY"
    assert state["consecutive_failures"] == 0


def test_lexical_similarity(coordinator):
    sim = coordinator._lexical_similarity(
        "AI automation for business growth",
        "AI automation for revenue growth"
    )
    assert 0.5 < sim < 1.0


def test_check_diversity_under_threshold(coordinator, temp_db):
    result = coordinator.check_diversity("Unique title about Python", "Unique description about coding")
    assert result["safe"] is True


def test_check_diversity_over_threshold(coordinator, temp_db):
    # Insere publicação anterior no evento
    with temp_db._get_conn() as conn:
        c = conn.cursor()
        payload = json.dumps({"title": "AI automation tools for growth", "description": "Description about AI"})
        c.execute(
            "INSERT INTO experiment_events (experiment_id, timestamp, event_type, payload_json) VALUES (?, ?, ?, ?)",
            ("EXP-001", datetime.now(timezone.utc).isoformat(), "PUBLISH_CONTENT", payload)
        )
        conn.commit()
    
    result = coordinator.check_diversity("AI automation tools for growth", "Another description")
    assert result["safe"] is False


def test_check_page_anomalies_login(coordinator):
    page_mock = MagicMock()
    page_mock.url = "https://www.pinterest.com/login"
    anomaly = coordinator.check_page_anomalies(page_mock)
    assert anomaly == "LOGIN_REQUIRED"


def test_check_page_anomalies_captcha(coordinator):
    page_mock = MagicMock()
    page_mock.url = "https://www.pinterest.com/pin-builder"
    page_mock.locator.return_value.first.is_visible.return_value = False
    
    def side_effect(selector):
        loc = MagicMock()
        if "recaptcha" in selector:
            loc.first.is_visible.return_value = True
        else:
            loc.first.is_visible.return_value = False
        return loc
        
    page_mock.locator.side_effect = side_effect
    anomaly = coordinator.check_page_anomalies(page_mock)
    assert anomaly == "CAPTCHA_DETECTED"


def test_check_page_anomalies_429(coordinator):
    page_mock = MagicMock()
    page_mock.url = "https://www.pinterest.com/pin-builder"
    page_mock.locator.return_value.first.is_visible.return_value = False
    
    body_loc = MagicMock()
    body_loc.inner_text.return_value = "Too many requests. Limit exceeded."
    
    def side_effect(selector):
        if selector == "body":
            return body_loc
        loc = MagicMock()
        loc.first.is_visible.return_value = False
        return loc
        
    page_mock.locator.side_effect = side_effect
    anomaly = coordinator.check_page_anomalies(page_mock)
    assert anomaly == "RATE_LIMIT_429"


def test_handle_publish_result_success(coordinator):
    coordinator.handle_publish_result(success=True)
    state = coordinator.get_state()
    assert state["state"] == "HEALTHY"
    assert state["total_posts"] == 1
    assert state["total_successes"] == 1


def test_handle_publish_result_consecutive_failures(coordinator):
    coordinator.handle_publish_result(success=False, error_type="PUBLISH_SLOW")
    state = coordinator.get_state()
    assert state["consecutive_failures"] == 1
    
    coordinator.handle_publish_result(success=False, error_type="PUBLISH_SLOW")
    state = coordinator.get_state()
    assert state["consecutive_failures"] == 2


def test_handle_publish_result_critical_error(coordinator):
    coordinator.handle_publish_result(success=False, error_type="CAPTCHA_DETECTED")
    state = coordinator.get_state()
    assert state["state"] == "COOLDOWN"
    assert state["cooldown_until"] is not None


def test_cooldown_expiration(coordinator, temp_db):
    past_time = (datetime.now(timezone.utc) - timedelta(hours=25)).strftime("%Y-%m-%dT%H:%M:%SZ")
    state = coordinator.get_state()
    state["state"] = "COOLDOWN"
    state["trust_score"] = 45  # After +10 recovery → 55 (WARNING, not COOLDOWN)
    state["consecutive_failures"] = 3
    state["cooldown_until"] = past_time
    temp_db.set_system_state("PINTEREST_ACC_STATE", state)
    
    current_state = coordinator.get_state()
    assert current_state["state"] != "COOLDOWN"
    assert current_state["trust_score"] == 55  # +10 recovery
    assert current_state["consecutive_failures"] == 0
    assert current_state["cooldown_until"] is None
