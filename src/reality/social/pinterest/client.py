import os
import time
import uuid
import base64
import logging
import requests
from typing import Dict, Any, List

from dotenv import load_dotenv
load_dotenv()

from src.reality.base import Publisher, MetricsProvider, PublishedContent, CanonicalMetrics
from src.reality.social.pinterest.auth import PinterestAuth
from src.reality.social.pinterest.errors import PinterestError, PinterestAuthError
from src.reality.social.pinterest.rate_limit import RateLimitManager
from src.reality.social.pinterest.uploader import VideoUploader
from src.reality.social.pinterest.analytics import AnalyticsManager

# Logger estruturado de observabilidade
obs_logger = logging.getLogger("observability.pinterest")
obs_logger.setLevel(logging.INFO)

class PinterestClient(Publisher, MetricsProvider):
    """
    Cliente concreto do Pinterest, operando como provedor de Realidade.
    """
    
    provider_name = "pinterest_api"
    confidence_score = 0.99
    reliability_score = 0.99
    supported_capabilities = ["publish_image", "publish_video", "get_metrics", "archive_content"]
    cost_per_action = 0.0
    latency_ms = 150
    
    def __init__(self, mode: str = None, board_id: str = None, access_token: str = None):
        self.mode = mode or os.getenv("PINTEREST_MODE", "shadow").lower()
        self.board_id = board_id or os.getenv("PINTEREST_BOARD_ID")
        
        self.auth = PinterestAuth(access_token)
        self.headers = self.auth.get_auth_headers()
        
        self.rate_limit_mgr = RateLimitManager()
        self.uploader = VideoUploader(self.headers, self.rate_limit_mgr)
        self.analytics_mgr = AnalyticsManager(self.headers, self.rate_limit_mgr)

    def health(self) -> Dict[str, Any]:
        """
        Verifica se o token é válido e se o board existe.
        """
        start_time = time.time()
        board_url = f"https://api.pinterest.com/v5/boards/{self.board_id}"
        self.rate_limit_mgr.check_and_wait("pinterest")
        
        try:
            response = requests.get(board_url, headers=self.headers)
            self._update_rate_limits(response.headers)
            latency = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                quota = response.headers.get("x-ratelimit-remaining")
                return {
                    "healthy": True,
                    "token": "ok",
                    "board": "ok",
                    "quota_remaining": int(quota) if quota is not None else None,
                    "latency_ms": latency
                }
            else:
                return {
                    "healthy": False,
                    "token": f"error_status_{response.status_code}",
                    "board": f"error_status_{response.status_code}",
                    "latency_ms": latency
                }
        except Exception as e:
            return {
                "healthy": False,
                "token": "error_exception",
                "board": "error_exception",
                "error": str(e),
                "latency_ms": int((time.time() - start_time) * 1000)
            }

    def publish_image(self, image_path: str, title: str, description: str, destination_link: str) -> PublishedContent:
        """
        Publica uma imagem local usando Base64.
        """
        t0 = time.time()
        
        if self.mode == "shadow":
            mock_id = f"SHADOW-PIN-{uuid.uuid4().hex[:8].upper()}"
            self._log_observability("publish_image", t0, "success", mock_id)
            return PublishedContent(
                content_id=mock_id,
                platform="pinterest",
                status="shadow_mode",
                url="https://pinterest.com/shadow"
            )
            
        # Converter imagem para Base64
        try:
            with open(image_path, "rb") as image_file:
                img_data = base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            raise PinterestError(f"Erro ao carregar imagem para codificação Base64: {str(e)}")

        ext = os.path.splitext(image_path)[1].lower()
        content_type = "image/png" if ext == ".png" else "image/jpeg"

        url = "https://api.pinterest.com/v5/pins"
        payload = {
            "board_id": self.board_id,
            "title": title,
            "description": description,
            "link": destination_link,
            "media_source": {
                "source_type": "image_base64",
                "content_type": content_type,
                "data": img_data
            }
        }

        self.rate_limit_mgr.check_and_wait("pinterest")
        response = requests.post(url, json=payload, headers=self.headers)
        self._update_rate_limits(response.headers)

        if response.status_code == 429:
            reset_ts = float(response.headers.get("x-ratelimit-reset", time.time() + 60))
            self.rate_limit_mgr.handle_rate_limit_error("pinterest", reset_ts)
            response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code != 201:
            self._log_observability("publish_image", t0, "failure", error_msg=response.text)
            raise PinterestError(f"Erro ao publicar imagem no Pinterest: {response.text}")

        res_data = response.json()
        pin_id = res_data["id"]
        self._log_observability("publish_image", t0, "success", pin_id)
        
        return PublishedContent(
            content_id=pin_id,
            platform="pinterest",
            status="published",
            published_at=res_data.get("created_at"),
            url=f"https://www.pinterest.com/pin/{pin_id}/"
        )

    def publish_video(self, video_path: str, title: str, description: str, destination_link: str) -> PublishedContent:
        """
        Publica um vídeo local usando o pipeline de upload e polling.
        """
        t0 = time.time()
        
        if self.mode == "shadow":
            mock_id = f"SHADOW-PIN-{uuid.uuid4().hex[:8].upper()}"
            self._log_observability("publish_video", t0, "success", mock_id)
            return PublishedContent(
                content_id=mock_id,
                platform="pinterest",
                status="shadow_mode",
                url="https://pinterest.com/shadow"
            )

        # 1. Faz upload do vídeo
        media_id = self.uploader.upload_video(video_path)

        # 2. Cria o Pin associado à mídia
        url = "https://api.pinterest.com/v5/pins"
        payload = {
            "board_id": self.board_id,
            "title": title,
            "description": description,
            "link": destination_link,
            "media_source": {
                "source_type": "video_id",
                "cover_image_url": "https://i.imgur.com/mock.jpg", # Placeholder para cover obrigatório
                "media_id": media_id
            }
        }

        self.rate_limit_mgr.check_and_wait("pinterest")
        response = requests.post(url, json=payload, headers=self.headers)
        self._update_rate_limits(response.headers)

        if response.status_code == 429:
            reset_ts = float(response.headers.get("x-ratelimit-reset", time.time() + 60))
            self.rate_limit_mgr.handle_rate_limit_error("pinterest", reset_ts)
            response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code != 201:
            self._log_observability("publish_video", t0, "failure", error_msg=response.text)
            raise PinterestError(f"Erro ao criar Pin de vídeo no Pinterest: {response.text}")

        res_data = response.json()
        pin_id = res_data["id"]
        self._log_observability("publish_video", t0, "success", pin_id)

        return PublishedContent(
            content_id=pin_id,
            platform="pinterest",
            status="published",
            published_at=res_data.get("created_at"),
            url=f"https://www.pinterest.com/pin/{pin_id}/"
        )

    def get_metrics(self, content_id: str) -> CanonicalMetrics:
        """
        Retorna as métricas canônicas, servindo do cache ou fazendo requisição.
        """
        t0 = time.time()
        try:
            metrics = self.analytics_mgr.get_metrics(content_id)
            self._log_observability("get_metrics", t0, "success", content_id)
            return metrics
        except Exception as e:
            self._log_observability("get_metrics", t0, "failure", content_id, error_msg=str(e))
            raise e

    def archive_content(self, content_id: str) -> bool:
        """
        Exclui o Pin do Pinterest (equivalente ao arquivamento).
        """
        t0 = time.time()
        
        if self.mode == "shadow":
            self._log_observability("archive_content", t0, "success", content_id)
            return True
            
        url = f"https://api.pinterest.com/v5/pins/{content_id}"
        self.rate_limit_mgr.check_and_wait("pinterest")
        response = requests.delete(url, headers=self.headers)
        self._update_rate_limits(response.headers)
        
        if response.status_code == 429:
            reset_ts = float(response.headers.get("x-ratelimit-reset", time.time() + 60))
            self.rate_limit_mgr.handle_rate_limit_error("pinterest", reset_ts)
            response = requests.delete(url, headers=self.headers)

        if response.status_code != 204:
            self._log_observability("archive_content", t0, "failure", content_id, error_msg=response.text)
            raise PinterestError(f"Erro ao arquivar/deletar Pin {content_id}: {response.text}")

        self._log_observability("archive_content", t0, "success", content_id)
        return True

    def _update_rate_limits(self, headers: Dict[str, str]):
        limit = headers.get("x-ratelimit-limit")
        remaining = headers.get("x-ratelimit-remaining")
        reset = headers.get("x-ratelimit-reset")
        if limit and remaining and reset:
            self.rate_limit_mgr.update_limits("pinterest", limit, remaining, reset)

    def _log_observability(self, operation: str, start_time: float, status: str, pin_id: str = None, error_msg: str = None):
        latency = int((time.time() - start_time) * 1000)
        event = {
            "provider": "pinterest",
            "operation": operation,
            "latency_ms": latency,
            "status": status
        }
        if pin_id:
            event["pin_id"] = pin_id
        if error_msg:
            event["error"] = error_msg
            
        # Loga estruturado como JSON string
        import json
        obs_logger.info(json.dumps(event))
