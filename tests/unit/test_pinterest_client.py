import os
import time
import pytest
import tempfile
import sqlite3
from unittest.mock import MagicMock, patch

from src.reality.base import PublishedContent, CanonicalMetrics
from src.reality.social.pinterest.client import PinterestClient
from src.integrations.pinterest.errors import PinterestError, PinterestAuthError, PinterestRateLimitError, UploadTimeoutError
from src.integrations.pinterest.rate_limit import RateLimitManager
from src.integrations.pinterest.uploader import VideoUploader
from src.integrations.pinterest.analytics import AnalyticsManager

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {
        "PINTEREST_ACCESS_TOKEN": "test_token_12345",
        "PINTEREST_BOARD_ID": "board_98765",
        "PINTEREST_MODE": "shadow"
    }):
        yield

def test_client_init_and_auth_headers(mock_env):
    client = PinterestClient()
    assert client.mode == "shadow"
    assert client.board_id == "board_98765"
    
    headers = client.headers
    assert headers["Authorization"] == "Bearer test_token_12345"
    assert headers["Accept"] == "application/json"

def test_client_init_missing_token():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(PinterestAuthError):
            PinterestClient()

def test_client_shadow_publish(mock_env):
    client = PinterestClient()
    
    res_img = client.publish_image("dummy_path.png", "Title", "Desc", "http://link.com")
    assert isinstance(res_img, PublishedContent)
    assert "SHADOW-PIN-" in res_img.content_id
    assert res_img.status == "shadow_mode"
    
    res_vid = client.publish_video("dummy_path.mp4", "Title", "Desc", "http://link.com")
    assert isinstance(res_vid, PublishedContent)
    assert "SHADOW-PIN-" in res_vid.content_id
    assert res_vid.status == "shadow_mode"

@patch("requests.get")
def test_client_health(mock_get, mock_env):
    client = PinterestClient()
    
    # Simula resposta de sucesso do board diretamente
    mock_resp_board = MagicMock()
    mock_resp_board.status_code = 200
    mock_resp_board.headers = {"x-ratelimit-limit": "1000", "x-ratelimit-remaining": "998", "x-ratelimit-reset": str(time.time() + 60)}
    
    mock_get.return_value = mock_resp_board
    
    health = client.health()
    assert health["healthy"] is True
    assert health["token"] == "ok"
    assert health["board"] == "ok"
    assert health["quota_remaining"] == 998

@patch("requests.post")
def test_client_live_publish_image(mock_post, mock_env):
    client = PinterestClient(mode="live")
    
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "id": "111222333",
        "created_at": "2026-07-12T19:00:00Z"
    }
    mock_resp.headers = {}
    mock_post.return_value = mock_resp
    
    # Criar arquivo temporário para simular imagem
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"fake_image_data")
        temp_img_path = f.name
        
    try:
        res = client.publish_image(temp_img_path, "Live Title", "Live Desc", "http://example.com")
        assert res.content_id == "111222333"
        assert res.status == "published"
        assert res.url == "https://www.pinterest.com/pin/111222333/"
    finally:
        os.remove(temp_img_path)

@patch("requests.post")
@patch("requests.get")
def test_client_live_publish_video_success(mock_get, mock_post, mock_env):
    client = PinterestClient(mode="live")
    
    # Mock do Registro de Media (POST /media)
    mock_resp_reg = MagicMock()
    mock_resp_reg.status_code = 201
    mock_resp_reg.json.return_value = {
        "media_id": "vid_media_id_777",
        "upload_url": "https://s3.amazonaws.com/mock-upload",
        "upload_parameters": {"key": "value"}
    }
    mock_resp_reg.headers = {}
    
    # Mock do POST S3
    mock_resp_s3 = MagicMock()
    mock_resp_s3.status_code = 204
    
    # Mock do Pin Creation (POST /pins)
    mock_resp_pin = MagicMock()
    mock_resp_pin.status_code = 201
    mock_resp_pin.json.return_value = {
        "id": "pin_vid_888",
        "created_at": "2026-07-12T19:00:00Z"
    }
    mock_resp_pin.headers = {}
    
    mock_post.side_effect = [mock_resp_reg, mock_resp_s3, mock_resp_pin]
    
    # Mock do Polling (GET /media/{media_id})
    mock_resp_poll = MagicMock()
    mock_resp_poll.status_code = 200
    mock_resp_poll.json.return_value = {"status": "succeeded"}
    mock_resp_poll.headers = {}
    mock_get.return_value = mock_resp_poll
    
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(b"fake_video_data")
        temp_vid_path = f.name
        
    try:
        # Patch time.sleep no uploader para não atrasar o teste
        with patch("time.sleep"):
            res = client.publish_video(temp_vid_path, "Vid Title", "Vid Desc", "http://example.com")
            
        assert res.content_id == "pin_vid_888"
        assert res.status == "published"
    finally:
        os.remove(temp_vid_path)

@patch("requests.post")
@patch("requests.get")
def test_client_live_publish_video_polling_timeout(mock_get, mock_post, mock_env):
    client = PinterestClient(mode="live")
    
    # Mock do Registro de Media (POST /media)
    mock_resp_reg = MagicMock()
    mock_resp_reg.status_code = 201
    mock_resp_reg.json.return_value = {
        "media_id": "vid_media_id_777",
        "upload_url": "https://s3.amazonaws.com/mock-upload",
        "upload_parameters": {}
    }
    mock_resp_reg.headers = {}
    mock_post.side_effect = [mock_resp_reg, MagicMock(status_code=204)]
    
    # Mock do Polling retornando sempre "registered" (nunca conclui)
    mock_resp_poll = MagicMock()
    mock_resp_poll.status_code = 200
    mock_resp_poll.json.return_value = {"status": "registered"}
    mock_resp_poll.headers = {}
    mock_get.return_value = mock_resp_poll
    
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(b"fake_video_data")
        temp_vid_path = f.name
        
    try:
        with patch("time.sleep"):
            with pytest.raises(UploadTimeoutError):
                client.publish_video(temp_vid_path, "Vid Title", "Vid Desc", "http://example.com")
    finally:
        os.remove(temp_vid_path)

@patch("requests.get")
def test_analytics_cache_and_fetch(mock_get, mock_env):
    client = PinterestClient()
    # Injeta o banco temporário em memória
    client.analytics_mgr = AnalyticsManager(client.headers, client.rate_limit_mgr, ":memory:")
    
    # Simula resposta da API
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "all": {
            "summary_metrics": {
                "IMPRESSION": 5500,
                "OUTBOUND_CLICK": 220,
                "SAVE": 77
            }
        }
    }
    mock_resp.headers = {}
    mock_get.return_value = mock_resp
    
    # 1a chamada: Miss (chama a API)
    metrics1 = client.get_metrics("pin_abc_123")
    assert metrics1.impressions == 5500
    assert mock_get.call_count == 1
    
    # 2a chamada: Hit (não chama a API)
    metrics2 = client.get_metrics("pin_abc_123")
    assert metrics2.impressions == 5500
    assert mock_get.call_count == 1  # Continua 1

def test_rate_limit_manager_wait():
    manager = RateLimitManager(":memory:")
    
    # Limite expirado (remaining=0, reset em 5 segundos no futuro)
    future_ts = time.time() + 3.0
    manager.update_limits("pinterest", limit_val=100, remaining=0, reset_timestamp=future_ts)
    
    t0 = time.time()
    # Deve dormir ~3 segundos
    manager.check_and_wait("pinterest")
    elapsed = time.time() - t0
    
    assert elapsed >= 2.5



