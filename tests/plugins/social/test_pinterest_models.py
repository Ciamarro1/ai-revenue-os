from src.revenue_os.plugins.social.models import (
    PinterestConfig,
    PinterestPublishPayload,
    PinterestPublishResult,
    PinterestPluginHealth,
    PublicationJob
)

def test_pinterest_config_schema():
    cfg = PinterestConfig(mode="live", headless=False, max_retries=5)
    assert cfg.mode == "live"
    assert cfg.headless is False
    assert cfg.max_retries == 5
    assert "pinterest.json" in cfg.session_file_path

def test_pinterest_publish_payload_schema():
    p = PinterestPublishPayload(media_path="pin.png", title="Title", description="Desc", link="http://l")
    assert p.media_path == "pin.png"
    assert p.media_type == "image"

def test_pinterest_publish_result_schema():
    res = PinterestPublishResult(
        pin_id="P1", url="http://pin/1", status="published", classification_status="REAL_PRODUCTION"
    )
    assert res.pin_id == "P1"
    assert res.classification_status == "REAL_PRODUCTION"

def test_publication_job_schema():
    payload = PinterestPublishPayload(media_path="p.png", title="t", description="d", link="l")
    job = PublicationJob(job_id="J1", payload=payload)
    assert job.job_id == "J1"
    assert job.status == "QUEUED"
