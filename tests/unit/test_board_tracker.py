import pytest
from src.revenue_os.analytics.database import ExperimentDatabase
from src.reality.social.pinterest.board_tracker import BoardTracker


@pytest.fixture
def temp_db():
    return ExperimentDatabase(":memory:")


@pytest.fixture
def tracker(temp_db):
    return BoardTracker(db=temp_db)


def test_record_publish(tracker):
    tracker.record_publish("AI Revenue OS", "EXP-001")
    stats = tracker.get_board_stats()
    assert len(stats) == 1
    assert stats[0]["board_name"] == "AI Revenue OS"
    assert stats[0]["total_posts"] == 1


def test_record_multiple_publishes(tracker):
    tracker.record_publish("AI Revenue OS", "EXP-001")
    tracker.record_publish("AI Revenue OS", "EXP-002")
    tracker.record_publish("AI Revenue OS", "EXP-003")
    stats = tracker.get_board_stats()
    assert stats[0]["total_posts"] == 3


def test_update_metrics(tracker):
    tracker.record_publish("AI Revenue OS", "EXP-001")
    tracker.update_metrics("AI Revenue OS", impressions=1000, clicks=50, saves=30)
    stats = tracker.get_board_stats()
    assert stats[0]["total_impressions"] == 1000
    assert stats[0]["total_clicks"] == 50
    assert stats[0]["total_saves"] == 30


def test_get_best_board_default(tracker):
    best = tracker.get_best_board()
    assert best == "AI Revenue OS"  # Default quando vazio


def test_get_best_board_by_ctr(tracker):
    tracker.record_publish("Board A", "EXP-001")
    tracker.record_publish("Board B", "EXP-002")
    tracker.update_metrics("Board A", impressions=1000, clicks=10, saves=5)
    tracker.update_metrics("Board B", impressions=1000, clicks=100, saves=50)
    best = tracker.get_best_board()
    assert best == "Board B"


def test_board_trust_score(tracker):
    tracker.record_publish("AI Revenue OS", "EXP-001")
    tracker.update_board_trust("AI Revenue OS", -20)
    stats = tracker.get_board_stats()
    assert stats[0]["trust_score"] == 80


def test_board_trust_floor(tracker):
    tracker.record_publish("AI Revenue OS", "EXP-001")
    tracker.update_board_trust("AI Revenue OS", -200)
    stats = tracker.get_board_stats()
    assert stats[0]["trust_score"] == 0


def test_multiple_boards(tracker):
    tracker.record_publish("AI Revenue OS", "EXP-001")
    tracker.record_publish("AI Automation", "EXP-002")
    tracker.record_publish("Python Tips", "EXP-003")
    stats = tracker.get_board_stats()
    assert len(stats) == 3
