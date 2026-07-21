import pytest
from src.revenue_os.analytics.database import ExperimentDatabase
from src.execution.queue_worker import QueueWorker


@pytest.fixture
def temp_db():
    db = ExperimentDatabase(":memory:")
    return db


@pytest.fixture
def worker(temp_db):
    return QueueWorker(db=temp_db)


def test_enqueue(worker):
    job_id = worker.enqueue("EXP-001", "/path/image.jpg", "Test Title", "Test Desc", "https://example.com")
    assert job_id.startswith("JOB-")


def test_enqueue_and_get(worker):
    worker.enqueue("EXP-001", "/path/image.jpg", "Title", "Desc", "https://example.com")
    job = worker.get_next_job()
    assert job is not None
    assert job["experiment_id"] == "EXP-001"
    assert job["status"] == "pending"
    assert job["title"] == "Title"


def test_process_next(worker, temp_db):
    worker.enqueue("EXP-001", "/path/image.jpg", "Title", "Desc", "https://example.com")
    job = worker.process_next()
    assert job is not None
    assert job["experiment_id"] == "EXP-001"
    
    # Verify job is marked as processing in database
    with temp_db._get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT status FROM publication_queue WHERE job_id = ?", (job["job_id"],))
        assert c.fetchone()[0] == "processing"


def test_process_next_cooldown(worker, temp_db):
    from src.reality.social.pinterest.safety_coordinator import PinterestSafetyCoordinator
    coord = PinterestSafetyCoordinator(db=temp_db)
    state = coord.get_state()
    state["state"] = "COOLDOWN"
    temp_db.set_system_state("PINTEREST_ACC_STATE", state)
    
    worker.enqueue("EXP-001", "/path/image.jpg", "Title", "Desc", "https://example.com")
    job = worker.process_next()
    assert job is None


def test_get_next_returns_none_empty_queue(worker):
    job = worker.get_next_job()
    assert job is None


def test_mark_processing(worker):
    job_id = worker.enqueue("EXP-001", "/path/image.jpg", "Title", "Desc", "https://example.com")
    worker.mark_processing(job_id)
    
    # Pending queue should be empty now
    job = worker.get_next_job()
    assert job is None


def test_mark_published(worker):
    job_id = worker.enqueue("EXP-001", "/path/image.jpg", "Title", "Desc", "https://example.com")
    worker.mark_published(job_id)
    stats = worker.get_queue_stats()
    assert stats["pending"] == 0


def test_mark_failed(worker):
    job_id = worker.enqueue("EXP-001", "/path/image.jpg", "Title", "Desc", "https://example.com")
    worker.mark_failed(job_id, "TEST_ERROR")
    stats = worker.get_queue_stats()
    assert stats["pending"] == 0


def test_recover_stale_jobs(worker):
    job_id = worker.enqueue("EXP-001", "/path/image.jpg", "Title", "Desc", "https://example.com")
    worker.mark_processing(job_id)
    
    # Simulate crash recovery
    worker.recover_stale_jobs()
    
    # Job should be back to pending
    job = worker.get_next_job()
    assert job is not None
    assert job["status"] == "pending"


def test_queue_stats(worker):
    worker.enqueue("EXP-001", "/p/1.jpg", "T1", "D1", "https://e.com")
    worker.enqueue("EXP-002", "/p/2.jpg", "T2", "D2", "https://e.com")
    worker.enqueue("EXP-003", "/p/3.jpg", "T3", "D3", "https://e.com")
    
    stats = worker.get_queue_stats()
    assert stats["pending"] == 3
    assert stats["total"] == 3


def test_scheduled_in_future(worker):
    """Jobs agendados no futuro não são retornados."""
    worker.enqueue("EXP-001", "/p/1.jpg", "T1", "D1", "https://e.com", scheduled_at="2099-01-01T00:00:00Z")
    job = worker.get_next_job()
    assert job is None
