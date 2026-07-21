import os
import pytest
from pathlib import Path

@pytest.fixture
def mock_html_path() -> Path:
    return Path(__file__).parent / "mock_pinterest.html"

@pytest.fixture
def mock_pin_page_path() -> Path:
    return Path(__file__).parent / "pin" / "12345" / "index.html"

@pytest.fixture
def dummy_image(tmp_path) -> Path:
    img_path = tmp_path / "test_image.jpg"
    # Escreve um cabeçalho JPEG mínimo válido para passar pelas validações de arquivo
    with open(img_path, "wb") as f:
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xd9')
    return img_path

@pytest.fixture
def dummy_video(tmp_path) -> Path:
    vid_path = tmp_path / "test_video.mp4"
    # Escreve um arquivo de vídeo falso (cabeçalho mp4 mínimo)
    with open(vid_path, "wb") as f:
        f.write(b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom')
    return vid_path

@pytest.fixture
def live_session_path() -> Path:
    return Path("config/sessions/pinterest.json")

@pytest.fixture
def has_live_session(live_session_path) -> bool:
    return live_session_path.exists()
