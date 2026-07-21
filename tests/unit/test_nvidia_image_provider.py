import os
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.factory.schemas import CreativeBrief, GeneratedAsset
from src.factory.image.nvidia.provider import NvidiaImageProvider
from src.factory.quality.image_gate import ImageQualityGate


MOCK_BRIEF = CreativeBrief(
    hypothesis_id="H-TEST-001",
    audience="entrepreneurs",
    emotion="curiosity",
    hook="Você sabia que 90% das pessoas ignoram esta estratégia?",
    format="static_image",
    duration=0,
    platform="pinterest",
    search_terms=["produtividade", "foco"],
    subject="produtividade matinal"
)


# ---------------------------------------------------------------------------
# NvidiaImageProvider — testes unitários (API mockada)
# ---------------------------------------------------------------------------

class TestNvidiaImageProvider:

    def test_health_no_key(self):
        """Sem API key, health deve reportar unhealthy sem explodir."""
        provider = NvidiaImageProvider(api_key=None)
        with patch.dict(os.environ, {}, clear=True):
            provider.api_key = None
            result = provider.health()
        assert result["healthy"] is False
        assert "NVIDIA_API_KEY" in result["error"]

    def test_health_with_key(self):
        """Com API key válida, health deve reportar healthy."""
        provider = NvidiaImageProvider(api_key="nvapi-fake-key-for-test")
        result = provider.health()
        assert result["healthy"] is True
        assert result["provider"] == "nvidia_flux1_dev"
        assert result["model"] == "flux.1-dev"

    def test_generate_no_key_raises_fatal(self):
        """Sem API key, generate deve levantar FatalError (não deve tentar chamada de rede)."""
        from src.services.exceptions import FatalError
        provider = NvidiaImageProvider(api_key=None)
        provider.api_key = None
        with pytest.raises(FatalError) as exc_info:
            provider.generate(MOCK_BRIEF)
        assert "NVIDIA_API_KEY" in str(exc_info.value)

    def test_generate_success(self, tmp_path):
        """Simula resposta bem-sucedida da API NVIDIA e verifica o GeneratedAsset."""
        import base64
        # JPEG mínimo válido (1x1 pixel, 631 bytes) em base64
        tiny_jpeg_b64 = (
            "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoH"
            "BwYIDAoMCwsKCwsNCxAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQME"
            "BAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU"
            "FBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/"
            "EABQQAQAAAAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEB"
            "AAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AJQAB/9k="
        )
        fake_response = {
            "artifacts": [{"base64": tiny_jpeg_b64}]
        }

        provider = NvidiaImageProvider(api_key="nvapi-fake-key", output_dir=str(tmp_path))
        # Limpar cache para forçar chamada à API
        with patch("src.factory.image.nvidia.provider.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = fake_response

            asset = provider.generate(MOCK_BRIEF)

        assert asset is not None
        assert asset.path.endswith(".jpg")
        assert asset.provider == "nvidia_flux1_dev"
        assert asset.resolution == "1024x1024"
        assert asset.approved_title is not None
        assert asset.approved_description is not None
        assert "pinterest" in asset.approved_title.lower() or len(asset.approved_title) > 0

    def test_generate_rate_limit_raises_retryable(self, tmp_path):
        """Rate limit (429) deve levantar RetryableError."""
        from src.services.exceptions import RetryableError
        provider = NvidiaImageProvider(api_key="nvapi-fake-key", output_dir=str(tmp_path))
        with patch("src.factory.image.nvidia.provider.requests.post") as mock_post:
            mock_post.return_value.status_code = 429
            mock_post.return_value.text = "Too Many Requests"
            with pytest.raises(RetryableError) as exc_info:
                provider.generate(MOCK_BRIEF)
        assert "RATE_LIMIT" in str(exc_info.value) or "rate" in str(exc_info.value).lower()

    def test_generate_api_error_raises_retryable(self, tmp_path):
        """Erro de API (500) deve levantar RetryableError."""
        from src.services.exceptions import RetryableError
        provider = NvidiaImageProvider(api_key="nvapi-fake-key", output_dir=str(tmp_path))
        with patch("src.factory.image.nvidia.provider.requests.post") as mock_post:
            mock_post.return_value.status_code = 500
            mock_post.return_value.text = "Internal Server Error"
            with pytest.raises(RetryableError):
                provider.generate(MOCK_BRIEF)

    def test_build_visual_prompt_contains_key_fields(self):
        """O prompt visual deve incluir sujeito, plataforma e emoção mapeada."""
        provider = NvidiaImageProvider(api_key="nvapi-fake")
        prompt = provider._build_visual_prompt(MOCK_BRIEF)
        assert "produtividade matinal" in prompt
        assert "pinterest" in prompt.lower()
        assert "mysterious" in prompt  # emotion="curiosity" mapeia para mysterious

    def test_cache_hit_returns_cached_asset(self, tmp_path):
        """Um render cacheado deve ser retornado sem chamar a API."""
        import base64
        tiny_jpeg_b64 = (
            "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoH"
            "BwYIDAoMCwsKCwsNCxAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQME"
            "BAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU"
            "FBQUFBQUFBT/wAARCAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/"
            "EABQQAQAAAAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEB"
            "AAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AJQAB/9k="
        )
        fake_response = {"artifacts": [{"base64": tiny_jpeg_b64}]}

        provider = NvidiaImageProvider(api_key="nvapi-fake-key", output_dir=str(tmp_path))

        with patch("src.factory.image.nvidia.provider.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = fake_response
            # Primeira chamada — gera e cacheia
            asset1 = provider.generate(MOCK_BRIEF)

        with patch("src.factory.image.nvidia.provider.requests.post") as mock_post2:
            mock_post2.return_value.status_code = 200
            mock_post2.return_value.json.return_value = fake_response
            # Segunda chamada — deve vir do cache
            asset2 = provider.generate(MOCK_BRIEF)
            # API não deve ter sido chamada de novo
            mock_post2.assert_not_called()

        assert asset1.path == asset2.path


# ---------------------------------------------------------------------------
# ImageQualityGate — testes unitários
# ---------------------------------------------------------------------------

class TestImageQualityGate:

    def _make_asset(self, path: str, title: str = "Título Aprovado", desc: str = "Descrição aprovada") -> GeneratedAsset:
        return GeneratedAsset(
            path=path,
            duration=0,
            resolution="1024x1536",
            provider="nvidia_flux1_dev",
            confidence=0.92,
            approved_title=title,
            approved_description=desc,
        )

    def test_passes_valid_image(self, tmp_path):
        """Uma imagem válida com conteúdo aprovado deve passar."""
        img = tmp_path / "pin.jpg"
        img.write_bytes(b"\xff\xd8\xff" + b"\x00" * (15 * 1024))  # 15KB fake JPEG header
        asset = self._make_asset(str(img))
        assert ImageQualityGate.check_quality(asset) is True

    def test_fails_missing_file(self, tmp_path):
        """Arquivo inexistente deve reprovar."""
        asset = self._make_asset(str(tmp_path / "ghost.jpg"))
        assert ImageQualityGate.check_quality(asset) is False

    def test_fails_too_small(self, tmp_path):
        """Arquivo menor que 10KB deve reprovar (provável corrupção)."""
        img = tmp_path / "tiny.jpg"
        img.write_bytes(b"\x00" * 100)  # apenas 100 bytes
        asset = self._make_asset(str(img))
        assert ImageQualityGate.check_quality(asset) is False

    def test_fails_invalid_extension(self, tmp_path):
        """Extensão inválida (ex: .mp4) deve reprovar no gate de imagem."""
        f = tmp_path / "video.mp4"
        f.write_bytes(b"\x00" * (20 * 1024))
        asset = self._make_asset(str(f))
        assert ImageQualityGate.check_quality(asset) is False

    def test_fails_missing_approved_title(self, tmp_path):
        """Imagem sem título aprovado deve reprovar — conteúdo não veio do Core."""
        img = tmp_path / "pin.png"
        img.write_bytes(b"\x89PNG" + b"\x00" * (15 * 1024))
        asset = self._make_asset(str(img), title="")
        assert ImageQualityGate.check_quality(asset) is False

    def test_fails_missing_approved_description(self, tmp_path):
        """Imagem sem descrição aprovada deve reprovar — conteúdo não veio do Core."""
        img = tmp_path / "pin.webp"
        img.write_bytes(b"RIFF" + b"\x00" * (15 * 1024))
        asset = self._make_asset(str(img), desc="")
        assert ImageQualityGate.check_quality(asset) is False
