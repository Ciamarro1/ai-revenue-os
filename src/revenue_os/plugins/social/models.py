from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class PinterestConfig(BaseModel):
    """
    Configuração Pydantic v2 para o PinterestPlugin.
    """
    mode: str = "shadow"  # shadow, live
    headless: bool = True
    max_retries: int = 3
    retry_backoff_sec: float = 2.0
    session_file_path: str = "config/sessions/pinterest.json"
    screenshots_dir: str = "storage/screenshots/pinterest"
    enable_vision_fallback: bool = True
    board_id: Optional[str] = None

class PinterestPublishPayload(BaseModel):
    """
    Payload de publicação de um Pin (Imagem ou Vídeo).
    """
    media_path: str
    title: str
    description: str
    link: str
    board_id: Optional[str] = None
    media_type: str = "image"  # image, video

class PinterestPublishResult(BaseModel):
    """
    Resultado da publicação de um Pin com captura de screenshot e classificação EDD.
    """
    pin_id: str
    url: str
    status: str  # published, shadow_mode, queued, failed
    provider_used: str = "pinterest_playwright"
    screenshot_path: Optional[str] = None
    published_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")
    classification_status: str = "WAITING_EXTERNAL_DEPENDENCY"  # REAL_PRODUCTION, LOCAL_TEST, WAITING_EXTERNAL_DEPENDENCY

class PublicationJob(BaseModel):
    """
    Job da Fila de Publicação do Pinterest.
    """
    job_id: str
    payload: PinterestPublishPayload
    status: str = "QUEUED"  # QUEUED, PROCESSING, COMPLETED, FAILED
    retry_count: int = 0
    result: Optional[PinterestPublishResult] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class PinterestPluginHealth(BaseModel):
    """
    Modelo de saúde e métricas do PinterestPlugin.
    """
    plugin_name: str = "pinterest_plugin"
    status: str = "HEALTHY"
    mode: str = "shadow"
    has_valid_session: bool = False
    has_api_credentials: bool = False
    pending_queue_count: int = 0
    message: str = "Operational"
