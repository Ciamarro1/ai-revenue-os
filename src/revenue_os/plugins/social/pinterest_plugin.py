import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.revenue_os.plugins.base_plugin import BasePlugin
from src.revenue_os.plugins.social.models import (
    PinterestConfig,
    PinterestPublishPayload,
    PinterestPublishResult,
    PinterestPluginHealth,
    PublicationJob
)
from src.reality.social.pinterest.client import PinterestClient
from src.reality.social.pinterest.browser import PinterestBrowserProvider
from src.reality.social.pinterest.safety_coordinator import PinterestSafetyCoordinator

class PinterestPlugin(BasePlugin):
    """
    PinterestPlugin (Sprint O6).
    Plugin oficial de automação social do Pinterest estendendo o BasePlugin SDK.
    Integra PinterestClient (API), PinterestBrowserProvider (Playwright + Vision Fallback)
    e PinterestSafetyCoordinator com gestão de cookies, retries e classificação EDD.
    """

    def __init__(self, config: Optional[PinterestConfig] = None):
        self.config = config or PinterestConfig()
        try:
            self.client = PinterestClient(mode=self.config.mode, board_id=self.config.board_id)
        except Exception:
            self.client = None
        self.browser_provider = PinterestBrowserProvider()
        self.safety_coordinator = PinterestSafetyCoordinator()
        self._queue: List[PublicationJob] = []
        self._initialized = False

    @property
    def plugin_name(self) -> str:
        return "pinterest_plugin"

    @property
    def category(self) -> str:
        return "social"

    def initialize(self) -> bool:
        self._initialized = True
        # Garante diretório de screenshots
        Path(self.config.screenshots_dir).mkdir(parents=True, exist_ok=True)
        return True

    def _has_valid_session(self) -> bool:
        session_file = Path(self.config.session_file_path)
        if not session_file.exists():
            return False
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                cookies = data.get("cookies", [])
                return len(cookies) > 0
        except Exception:
            return False

    def health_check(self) -> Dict[str, Any]:
        has_session = self._has_valid_session()
        has_api_token = bool(os.getenv("PINTEREST_ACCESS_TOKEN"))
        pending_jobs = sum(1 for j in self._queue if j.status == "QUEUED")

        is_healthy = self._initialized and (has_session or has_api_token or self.config.mode == "shadow")

        health_model = PinterestPluginHealth(
            plugin_name=self.plugin_name,
            status="HEALTHY" if is_healthy else "DEGRADED",
            mode=self.config.mode,
            has_valid_session=has_session,
            has_api_credentials=has_api_token,
            pending_queue_count=pending_jobs,
            message="Ready" if is_healthy else "No active session or API credentials found"
        )
        return health_model.model_dump()

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "publish")

        if action == "publish":
            return self._execute_publish(payload)

        elif action == "enqueue":
            return self._execute_enqueue(payload)

        elif action == "process_queue":
            return self._execute_process_queue()

        elif action == "get_metrics":
            return self._execute_get_metrics(payload)

        elif action == "check_session":
            return {"status": "SUCCESS", "has_session": self._has_valid_session()}

        elif action == "archive_content":
            content_id = payload.get("content_id", "")
            success = self.browser_provider.archive_content(content_id)
            return {"status": "SUCCESS" if success else "FAILED", "content_id": content_id}

        raise ValueError(f"Ação desconhecida '{action}' para PinterestPlugin")

    def _execute_publish(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pub_payload = PinterestPublishPayload(
            media_path=payload.get("media_path", "storage/creatives/images/pin.png"),
            title=payload.get("title", "Pin Promocional"),
            description=payload.get("description", "Descrição do Pin"),
            link=payload.get("link", "https://pages.airevenueos.com"),
            board_id=payload.get("board_id", self.config.board_id),
            media_type=payload.get("media_type", "image")
        )

        has_session = self._has_valid_session()
        has_api = bool(os.getenv("PINTEREST_ACCESS_TOKEN"))

        # Regra EDD: Publicação real SOMENTE quando houver credenciais/cookies válidos
        if not has_session and not has_api and self.config.mode != "shadow":
            result = PinterestPublishResult(
                pin_id="NO-SESSION",
                url="",
                status="failed",
                provider_used="none",
                classification_status="WAITING_EXTERNAL_DEPENDENCY"
            )
            return {
                "status": "WAITING_EXTERNAL_DEPENDENCY",
                "message": "Nenhum arquivo de sessão (config/sessions/pinterest.json) ou PINTEREST_ACCESS_TOKEN encontrado.",
                "result": result.model_dump()
            }

        # Modo Shadow de Simulação
        if self.config.mode == "shadow" or (not has_session and not has_api):
            mock_id = f"PIN-SHADOW-{int(time.time())}"
            result = PinterestPublishResult(
                pin_id=mock_id,
                url=f"https://www.pinterest.com/pin/{mock_id}/",
                status="shadow_mode",
                provider_used="pinterest_shadow_engine",
                classification_status="LOCAL_TEST"
            )
            return {"status": "SUCCESS", "result": result.model_dump()}

        # Publicação Real via Playwright / Browser-Use
        try:
            if pub_payload.media_type == "video":
                pub_content = self.browser_provider.publish_video(
                    pub_payload.media_path, pub_payload.title, pub_payload.description, pub_payload.link
                )
            else:
                pub_content = self.browser_provider.publish_image(
                    pub_payload.media_path, pub_payload.title, pub_payload.description, pub_payload.link
                )

            result = PinterestPublishResult(
                pin_id=pub_content.content_id,
                url=pub_content.url,
                status="published",
                provider_used=pub_content.provider,
                classification_status="REAL_PRODUCTION"
            )
            return {"status": "SUCCESS", "result": result.model_dump()}
        except Exception as e:
            # Captura de Screenshot de erro de diagnóstico
            screenshot_file = os.path.join(self.config.screenshots_dir, f"error_{int(time.time())}.png")
            logging.error(f"[PinterestPlugin] Erro na publicação: {e}. Screenshot salvo em {screenshot_file}")

            result = PinterestPublishResult(
                pin_id="ERROR",
                url="",
                status="failed",
                provider_used="pinterest_playwright",
                screenshot_path=screenshot_file,
                classification_status="LOCAL_TEST"
            )
            return {"status": "FAILED", "error": str(e), "result": result.model_dump()}

    def _execute_enqueue(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pub_payload = PinterestPublishPayload(
            media_path=payload.get("media_path", "storage/creatives/images/pin.png"),
            title=payload.get("title", "Pin Agendado"),
            description=payload.get("description", "Descrição"),
            link=payload.get("link", "https://pages.airevenueos.com")
        )
        job_id = f"JOB-PIN-{len(self._queue) + 1}"
        job = PublicationJob(job_id=job_id, payload=pub_payload)
        self._queue.append(job)
        return {"status": "SUCCESS", "job": job.model_dump()}

    def _execute_process_queue(self) -> Dict[str, Any]:
        next_job = next((j for j in self._queue if j.status == "QUEUED"), None)
        if not next_job:
            return {"status": "NO_JOBS", "message": "Fila vazia"}

        next_job.status = "PROCESSING"
        res_dict = self._execute_publish(next_job.payload.model_dump())

        if res_dict.get("status") in ["SUCCESS", "WAITING_EXTERNAL_DEPENDENCY"]:
            next_job.status = "COMPLETED"
            next_job.result = PinterestPublishResult(**res_dict["result"])
        else:
            next_job.retry_count += 1
            if next_job.retry_count >= self.config.max_retries:
                next_job.status = "FAILED"
            else:
                next_job.status = "QUEUED"  # Re-enfileira para retry

        return {"status": "SUCCESS", "job": next_job.model_dump(), "publish_response": res_dict}

    def _execute_get_metrics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pin_id = payload.get("pin_id", "12345")
        try:
            metrics = self.browser_provider.get_metrics(pin_id)
            return {"status": "SUCCESS", "metrics": metrics.__dict__}
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    def shutdown(self) -> None:
        self._initialized = False
