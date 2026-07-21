import pytest
from unittest.mock import MagicMock
from src.revenue_os.analytics.database import ExperimentDatabase
from src.factory.quality.image_dedup import ImageDeduplicator, HAS_IMAGEHASH


@pytest.fixture
def temp_db():
    return ExperimentDatabase(":memory:")


@pytest.fixture
def dedup(temp_db):
    return ImageDeduplicator(db=temp_db)


def test_table_created(dedup, temp_db):
    """Tabela image_hashes deve existir."""
    with temp_db._get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image_hashes'")
        assert c.fetchone() is not None


def test_no_duplicate_empty_db(dedup):
    """Sem hashes registrados, nenhuma imagem é duplicata."""
    result = dedup.is_duplicate("/nonexistent/image.jpg")
    assert result["duplicate"] is False


@pytest.mark.skipif(not HAS_IMAGEHASH, reason="imagehash não instalado")
def test_compute_hashes_nonexistent_file(dedup):
    """Hash de arquivo inexistente retorna None."""
    result = dedup.compute_hashes("/nonexistent/image.jpg")
    assert result is None


def test_register_and_check_without_imagehash(dedup):
    """Sem imagehash instalado, operações são graciosamente ignoradas."""
    if not HAS_IMAGEHASH:
        result = dedup.is_duplicate("/any/image.jpg")
        assert result["duplicate"] is False
        assert result.get("reason") == "imagehash_not_installed"
